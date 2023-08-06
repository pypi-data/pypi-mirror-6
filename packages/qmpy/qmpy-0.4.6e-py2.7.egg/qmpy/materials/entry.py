#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import os

from django.db import models
from django.db import transaction
import networkx as nx

from qmpy.db.custom import *
from qmpy.materials.composition import *
from qmpy.materials.element import Element, Species
from qmpy.materials.structure import Structure
from qmpy.utils import *
from qmpy.computing.resources import Project
from qmpy.data.meta_data import *
import qmpy.io as io
import qmpy.computing.scripts as scripts
import qmpy.analysis.vasp as vasp

k_desc = 'Descriptive keyword for looking up entries'
h_desc = 'A note indicating a reason the entry should not be calculated'
@add_meta_data('keyword', description=k_desc)
@add_meta_data('hold', description=h_desc)
class Entry(models.Model):
    """Base class for a database entry.

    The core model for typical database entries. An Entry model represents an
    input structure to the database, and can be created from any input file.
    The Entry also ties together all of the associated :mod:`qmpy.Structure`,
    :mod:`qmpy.Calculation`, :mod:`qmpy.Reference`,
    :mod:`qmpy.FormationEnergies`, and other associated databas entries.

    Relationships:
        | :mod:`~qmpy.Calculation` via calculation_set
        | :mod:`~qmpy.DOS` via dos_set
        | :mod:`~qmpy.Entry` via duplicate_of
        | :mod:`~qmpy.Entry` via duplicates
        | :mod:`~qmpy.Element` via element_set
        | :mod:`~qmpy.FormationEnergy` via formationenergy_set
        | :mod:`~qmpy.Job` via job_set
        | :mod:`~qmpy.MetaData` via meta_data
        | :mod:`~qmpy.Project` via project_set
        | :mod:`~qmpy.Prototype` via prototype
        | :mod:`~qmpy.Species` via species_set
        | :mod:`~qmpy.Structure` via structure_set
        | :mod:`~qmpy.Task` via task_set
        | :mod:`~qmpy.Reference` via reference
        | :mod:`~qmpy.Composition` via composition

    Attributes:
        | id: Primary key (auto-incrementing int)
        | natoms: Number of atoms in the primitive input cell
        | ntypes: Number of elements in the input structure
        | path: Path to input file, and location of subsequent calculations.
        | label: An identifying name for the structure. e.g. icsd-1001 or A3

    """
    ### structure properties
    path = models.CharField(max_length=255, unique=True)
    meta_data = models.ManyToManyField('MetaData')
    label = models.CharField(max_length=20, null=True)

    ### record keeping
    duplicate_of = models.ForeignKey('Entry', related_name='duplicates',
            null=True)
    ntypes = models.IntegerField(blank=True, null=True)
    natoms = models.IntegerField(blank=True, null=True)

    ### links
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    project_set = models.ManyToManyField('Project')
    composition = models.ForeignKey('Composition', blank=True, null=True)
    reference = models.ForeignKey('Reference', null=True, blank=True)
    prototype = models.ForeignKey('Prototype', null=True, blank=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'entries'

    def __str__(self):
        return '%s - %s' % (self.id, self.name)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Saves the Entry, as well as all associated objects."""
        if not self.reference is None:
            if self.reference.id is None:
                self.reference.save()
                self.reference = self.reference
        super(Entry, self).save(*args, **kwargs)
        for k, v in self.structures.items():
            v.label = k
        self.structure_set = self.structures.values()
        for k, v in self.calculations.items():
            v.label = k
        self.calculation_set = self.calculations.values()
        if self._elements:
            self.element_set = self.elements
        if self._species:
            self.species_set = self.species
        if self._projects:
            self.project_set = self.projects
        if self._keywords or self._holds:
            self.meta_data = self.hold_objects + self.keyword_objects

    @classmethod
    def create(cls, source, keywords=[], projects=[], **kwargs):
        """
        Create an Entry object from a provided input file.

        Keywords:
            keywords: list of keywords to associate with the entry.
            projects: list of project names to associate with the entry.

        """
        source_file = os.path.abspath(source)
        path = os.path.dirname(source_file)
        if Entry.objects.filter(path=path).exists():
            return Entry.objects.get(path=path)
        entry = cls(**kwargs)
        
        entry.source_file = source_file
        entry.path = os.path.dirname(source_file)
        structure = io.read(source_file)
        structure.make_primitive()

        entry.structures['input'] = structure
        if any([ a.occupancy < 0.95 for a in structure ]):
            entry.holds.append('partial occupancy')
        if not structure.composition == structure.reported_composition:
            entry.holds.append('composition mismatch in CIF')
            entry.composition = entry.input.reported_composition
        else:
            entry.composition = entry.input.composition

        entry.ntypes = structure.ntypes
        entry.natoms = len(structure.atoms)
        entry.elements = entry.comp.keys() 
        entry.reference = structure.reference
        entry.prototype = structure.prototype
        entry.keywords = keywords
        entry.projects = projects
        return entry

    _elements = None
    @property
    def elements(self):
        """List of Elements"""
        if self._elements is None:
            self._elements = [ Element.get(e) for e in self.comp.keys() ]
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = [ Element.get(e) for e in elements ]

    _species = None
    @property
    def species(self):
        """List of Species"""
        if self._species is None:
            self._species = [ Species.get(s) for s in self.spec_comp.keys() ]
        return self._species

    @species.setter
    def species(self, species):
        self._species = [ Species.get(e) for e in species ]

    _projects = None
    @property
    def projects(self):
        """List of Projects"""
        if self._projects is None:
            self._projects = list(self.project_set.all())
        return self._projects

    @projects.setter
    def projects(self, projects):
        self._projects = [ Project.get(p) for p in projects ]

    _structures = None
    @property
    def structures(self):
        if self._structures is None:
            if self.id is None:
                self._structures = {}
            else:
                structs = self.structure_set.exclude(label='')
                labels = [ s.label for s in structs ]
                if len(set(labels)) < len(labels):
                    print 'Warning! Some related objects have repeat names!'
                    print 'To address this, all labels have been appended',
                    print 'with the primary key of the related object.'
                    labels = [ '%s_%s' % (s.label, s.pk) for s in structs ]
                self._structures = dict((k, s) for k,s in zip(labels, structs))
        return self._structures

    @structures.setter
    def structures(self, structs):
        if not isinstance(structs, dict):
            raise TypeError('structures must be a dict')
        if not all( isinstance(v, Structure) for v in structs.values()):
            raise TypeError('structures must be a dict of Calculations')
        self._structures = structs

    @structures.deleter
    def structures(self, struct):
        self._structures[struct].delete()
        del self._structures[struct]

    _calculations = None
    @property
    def calculations(self):
        """Dictionary of label:Calculation pairs.""" 
        if self._calculations is None:
            if self.id is None:
                self._calculations = {}
            else:
                calcs = self.calculation_set.exclude(label='')
                labels = [ c.label for c in calcs ]
                if len(set(labels)) < len(labels):
                    print 'Warning! Some related objects have repeat names!'
                    print 'To address this, all labels have been appended',
                    print 'with the primary key of the related object.'
                    labels = [ '%s_%s' % (c.label, c.pk) for c in calcs ]
                self._calculations = dict((k, c) for k,c in zip(labels, calcs))
        return self._calculations

    @calculations.setter
    def calculations(self, calcs):
        if not isinstance(calcs, dict):
            raise TypeError('calculations must be a dict')
        if not all( isinstance(v, vasp.Calculation) for v in calcs.values()):
            raise TypeError('calculations must be a dict of Calculations')
        self._calculations = calcs

    @calculations.deleter
    def calculations(self, calc): 
        self._calculations[calc].delete()
        del self._calculations[calc]

    @property
    def input(self):
        return self.structures.get('input')

    @input.setter
    def input(self, structure):
        self.structures['input'] = structure

    @property
    def tasks(self):
        return list(self.task_set.all())

    @property
    def jobs(self):
        return list(self.job_set.all())

    @property
    def comp(self):
        if not self.composition_id is None:
            return parse_comp(self.composition_id)
        elif not self.input is None:
            return self.input.comp
        else:
            return {}

    @property
    def spec_comp(self):
        """
        Composition dictionary, using species (element + oxidation state)
        instead of just the elements.
        
        """
        if self.input is None:
            return {}
        else:
            return self.input.spec_comp

    @property
    def unit_comp(self):
        """Composition dictionary, normalized to 1 atom."""
        return normalize_comp(self.comp)

    @property
    def red_comp(self):
        """Composition dictionary, in reduced form."""
        return reduce_comp(self.comp)

    @property
    def name(self):
        """Unformatted name"""
        return format_comp(reduce_comp(self.comp))

    @property
    def latex(self):
        """LaTeX formatted name"""
        return format_latex(reduce_comp(self.comp))

    @property
    def html(self):
        """HTML formatted name"""
        return format_html(reduce_comp(self.comp))

    @property
    def proto_label(self):
        #if not self.prototype is None:
        #    return self.prototype.name
        similar = self.input.similar
        protos = []
        for s in similar:
            if not s.entry.prototype is None:
                protos.append(s.entry.prototype.name)
        protos = list(set(protos))
        if len(protos) == 1:
            return protos[0]
        else:
            return ', '.join(protos)

    @property
    def space(self):
        """Return the set of elements in the input structure.
        
        Example:
        >>> e = Entry.create("fe2o3/POSCAR") # an input containing Fe2O3
        >>> e.space
        set(["Fe", "O"])
        
        """
        return set([ e.symbol for e in self.elements])

    @property
    def total_energy(self):
        """
        If the structure has been relaxed, returns the formation energy of the
        final relaxed structure. Otherwise, returns None.

        """
        if 'static' in self.calculations:
            if self.calculations['static'].converged:
                return self.calculations['static'].energy_pa
        if 'standard' in self.calculations:
            if self.calculations['standard'].converged:
                return self.calculations['standard'].energy_pa
        return None

    @property
    def energy(self):
        """
        If the structure has been relaxed, returns the formation energy of the
        final relaxed structure. Otherwise, returns None.

        """
        if 'static' in self.calculations:
            if self.calculations['static'].converged:
                calc = self.calculations['static']
                f = calc.compute_formation()
                return f.delta_e
        if 'standard' in self.calculations:
            if self.calculations['standard'].converged:
                calc = self.calculations['standard']
                f = calc.compute_formation()
                return f.delta_e
        return None

    _history = None
    @property
    def history_graph(self):
        if self._history is None:
            G = nx.Graph()

            for c in self.calculation_set.all():
                G.add_edge(c.input, c.output, object=c)
            self._history = G
        return self._history

    @property
    def history(self):
        steps = []
        if 'static' in self.calculations:
            step = self.calculations['static']
        elif 'standard' in self.calculations:
            step = self.calculations['standard']
        while step:
            if isinstance(step, vasp.Calculation):
                step.type = 'calculation'
                steps.append(step)
                step = step.input
            if isinstance(step, Structure):
                step.type = 'structure'
                steps.append(step)
                try:
                    step = step.source.all()[0]
                except:
                    step = None
        return steps

    @property
    def spacegroup(self):
        for key in ['relaxed', 'fine_relaxed', 'input']:
            if key in self.structures:
                return self.structures[key].spacegroup

    @property
    def mass(self):
        """Return the mass of the entry, normalized to per atom."""
        return sum( Element.objects.get(symbol=elt).mass*amt for 
                elt, amt in self.unit_comp)

    @property
    def volume(self):
        """
        If the entry has gone through relaxation, returns the relaxed
        volume. Otherwise, returns the input volume.
        
        """
        if not self.relaxed is None:
            return self.relaxed.volume/self.natoms
        else:
            return self.input.volume/self.natoms

    @property
    def errors(self):
        """List of errors encountered in all calculations."""
        return dict( ( c.path, c.errors) for c in
                self.calculation_set.all() )

    @property
    def chg(self):
        """
        Attempts to load the charge density of the final calculation, if it is
        done. If not, returns False.

        """
        if not hasattr(self, '_chg'):
            if not self.done:
                self._chg = False
            else:
                self._chg = Grid.load_xdensity(self.path+'/standard/CHGCAR.gz')
        return self._chg

    def do(self, module, *args, **kwargs):
        """
        Looks for a computing script matching the first argument, and attempts
        to run it with itself as the first argument. Sends args and kwargs
        to the script. Should return a Calculation object, or list of
        Calculation objects. 

        Example:
        >>> e = Entry.objects.get(id=123)
        >>> e.do('relaxation')
        <Calculation: 523 @ relaxation settings>

        """
        script = getattr(scripts, module)
        return script(self, *args, **kwargs)

    def move(self, path):
        """
        Moves all calculation files to the specified path.

        """
        path = os.path.abspath(path)
        try:
            os.system('mv %s %s' % (self.path, path))
        except Exception, err:
            print err
            return
        self.path = path
        print 'Moved %s to %s' % (self, path)
        self.save()

    @property
    def running(self):
        return self.job_set.filter(state=1)

    def reset(self):
        """
        Deletes all calculations, removes all associated structures - returns
        the entry to a pristine state.

        """

        for structure in self.structures.values():
            if structure.label != 'input':
                structure.delete()

        self.calculation_set.all().delete()

        for task in self.tasks:
            task.state = 0 
            task.save()

        for job in self.job_set.filter(state=1):
            job.collect()
            job.delete()
        self.job_set.all().delete()

        for dir in os.listdir(self.path):
            if os.path.isdir(self.path+'/'+dir):
                print 'rm -rf %s/%s &> /dev/null' % (self.path, dir)
                os.system('rm -rf %s/%s &> /dev/null' % (self.path, dir))

    def visualize(self, structure='source'):
        """Attempts to open the input structure for visualization using VESTA"""
        os.system('VESTA %s/POSCAR' % self.path)

