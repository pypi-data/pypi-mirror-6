#!/usr/bin/env python

import numpy as np
from collections import defaultdict
import os.path
import time
import qmpy
import StringIO
import fractions as frac
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

THERMOPY_LIB_PATH = qmpy.INSTALL_PATH+'/data/thermodynamic/'

class PhaseError(Exception):
    pass

class PhaseDataError(Exception):
    pass

class PhaseData(object):
    """
    A PhaseData object is a container for storing and organizing phase data.
    Most importantly used when doing a large number of thermodynamic analyses
    and it is undesirable to access the database for every space you want to
    consider. 

    """
    def __init__(self):
        self.clear()

    @property
    def phases(self):
        """
        Return all phases.
        """
        return self._phases

    @phases.setter
    def phases(self, phases):
        self.clear()
        for phase in phases:
            self.add_phase(phase)

    def clear(self):
        self._phases = []
        self.phases_by_elt = defaultdict(set)
        self.phases_by_dim = defaultdict(set)
        self.phase_dict = {}
        self.space = set()

    def add_phase(self, phase):
        """
        Add a phase to the PhaseData collection. Updates the
        PhaseData.phase_dict and PhaseData.phases_by_elt dictionaries
        appropriately to enable quick access.

        Example:
        >>> pd = PhaseData()
        >>> pd.add_phase(Phase(composition='Fe2O3', energy=-3))
        >>> pd.add_phase(Phase(composition='Fe2O3', energy=-4))
        >>> pd.add_phase(Phase(composition='Fe2O3', energy=-5))
        >>> pd.phase_dict
        {'Fe2O3': <Phase Fe2O3 : -5}
        >>> pd.phases_by_elt['Fe']
        [<Phase Fe2O3 : -3>, <Phase Fe2O3 : -4>, <Phase Fe2O3 : -5>]
        """

        if not phase.name in self.phase_dict:
            self.phase_dict[phase.name] = phase
        elif abs(self.phase_dict[phase.name].energy - phase.energy) < 1e-3:
            return
        else:
            if phase.energy < self.phase_dict[phase.name].energy:
                self.phase_dict[phase.name] = phase
        self._phases.append(phase)
        phase.index = len(self._phases)

        for elt in phase.comp:
            self.phases_by_elt[elt].add(phase)
        self.phases_by_dim[len(phase.comp)].add(phase)

        self.space |= set(phase.comp.keys())

    def add_phases(self, phases):
        for phase in phases:
            self.add_phase(phase)

    def load_library(self, library):
        """
        Load a library file, containing self-consistent thermochemical data.
        
        """
        logger.debug('Loading Phases from %s' % library)
        self.read_file(qmpy.INSTALL_PATH+'/data/thermodata/'+library)

    def load_oqmd(self, space=None, search={}, stable=False, total=False):
        from qmpy.materials.formation_energy import FormationEnergy
        from qmpy.materials.element import Element
        logger.debug('Loading Phases from the OQMD')
        data = FormationEnergy.objects.exclude(delta_e=None, composition=None)
        if stable:
            data = data.exclude(stability__lte=0)
        if search:
            data = data.filter(**search)
        if space:
            space_qs = Element.objects.exclude(symbol__in=space)
            data = data.filter(composition__element_set__in=space)
            data = data.exclude(composition__element_set__in=space_qs)

        data = data.distinct()
        columns = [ 'id', 'composition_id', 'stability' ]
        if total:
            columns.append('calculation__energy_pa')
        else:
            columns.append('delta_e')

        values = data.values(*columns)

        for row in values:
            if not row['composition_id']:
                continue
            if total:
                energy = row['calculation__energy_pa']
            else:
                energy = row['delta_e']
            phase = Phase(energy=energy, 
                      composition=parse_comp(row['composition_id']),
                      #description=row['calculation__input__spacegroup'],
                      stability=row['stability'],
                      per_atom=True,
                      total=total)
            phase.id = row['id']
            self.add_phase(phase)

    def read_file(self, filename, per_atom=True):
        """
        Read in a thermodata file (named filename), formatted as 
        "composition energy [description]"

        E.g.

        composition energy
        Fe 0.0
        O 0.0
        Li 0.0
        Fe3O4 -0.21331204979
        FeO -0.589343204057
        Fe3O4 -0.21331204979
        FeLiO2 -0.446739168889
        FeLi5O4 -0.198830531099
        """
        if isinstance(filename, basestring):
            fileobj = open(filename)
        elif isinstance(filename, file):
            fileobj = filename
        elif isinstance(filename, type(StringIO.StringIO())):
            fileobj = filename
            fileobj.name = None
        thermodata = fileobj.readlines()
        headers = [ h.lower() for h in thermodata.pop(0).strip().split() ]
        if 'composition' not in headers:
            raise PhaseDataError("Found columns: %s. Must provide composition in\
                                  a column labelled composition." % 
                                  (', '.join(headers)))
        if ('energy' not in headers and 'delta_e' not in headers):
            raise PhaseDataError("Found columns: %s. Must provide energies in\
                                  a column labelled delta_e or energy." % 
                                  (', '.join(headers)))

        keywords = {'energy':'energy', 'composition':'composition', 
                'delta_e':'energy', 'delta_h':'energy', 'delta_g':'energy',
                'comp':'composition', 'name':'composition', 
                'desc':'description', 'description':'description'}

        headers = [ keywords[h] for h in headers if h in keywords ]

        name = filename.split('/')[-1]

        for i, line in enumerate(thermodata):
            line = line.strip().split()
            if not line:
                continue
            ddict = dict(zip(headers, line))
            phase = Phase(composition=ddict['composition'],
                          energy=float(ddict['energy']),
                          description=ddict.get('description', 
                              '{file}:{line}'.format(file=name, line=i)),
                          per_atom=per_atom)
            self.add_phase(phase)


    def get_phase_data(self, space):
        """
        Using an existing PhaseData object return a PhaseData object which is
        populated by returning a subset which is inside a given region of phase
        space.

        Example:
        >>> pd = PhaseData()
        >>> pd.read_file('legacy.dat')
        >>> new_pd = pd.get_phase_data(['Fe', 'O'])
        >>> new_pd.phase_dict

        """
        dim = len(space)
        phases = set(self.phases)
        others = set(self.phases_by_elt.keys()) - set(space)
        for elt in others:
            phases -= self.phases_by_elt[elt]
        pd = PhaseData()
        pd.phases = phases
        return pd

class Phase(object):
    """
    A Phase object is a point in composition-energy space. 

    Examples:
    >>> p = Phase('Fe2O3', -1.64, per_atom=True)
    >>> p2 = Phase('Fe2O3', -8.2, per_atom=False)
    >>> p3 = Phase({'Fe':0.4, 'O':0.6}, -1.64)
    >>> p4 = Phase({'Fe':6, 'O':9}, -24.6, per_atom=False)
    >>> p == p2
    True
    >>> p2 == p3
    True
    >>> p3 == p4
    True
    """

    id = None
    use = True
    show_label = True
    _calculation = None
    custom_name = None
    phase_dict = {}
    def __init__(self, 
            composition=None, 
            energy=None, 
            description='',
            per_atom=True,
            stability=None,
            total=False,
            name=''):

        if composition is None or energy is None:
            raise IncompletePhaseError
        if isinstance(composition, basestring):
            composition = parse_comp(composition)

        self._description = description
        self._comp = defaultdict(float, composition)
        self.stability = stability
        if name:
            self.custom_name = name

        if not per_atom:
            self._total_energy = energy
            self._energy = energy/sum(composition.values())
            self._energy_pfu = energy / sum(self.nom_comp.values())
        else:
            self._energy = energy
            self._total_energy = energy * sum(composition.values())
            self._energy_pfu = energy / sum(self.nom_comp.values())

        if len(self.comp) == 1 and not total:
            self._energy = 0.0
            self._total_energy = 0.0
            self._energy_pfu = 0.0

    @staticmethod
    def from_phases(phase_dict):
        """
        Generate a Phase object from a dictionary of Phase objects. Returns a
        composite phase of unit composition.
        """
        if len(phase_dict) == 1:
            return phase_dict.keys()[0]

        pkeys = sorted(phase_dict.keys(), key=lambda x: x.name)
        energy = sum([ amt*p.energy for p, amt in phase_dict.items() ])

        comp = defaultdict(float)
        for p, factor in phase_dict.items():
            for e, amt in p.unit_comp.items():
                comp[e] += amt*factor

        phase = Phase(
                composition=comp,
                energy=energy,
                per_atom=False)
        phase.phase_dict = phase_dict
        return phase

    @property
    def natoms(self):
        return sum(self.nom_comp.values())

    def __repr__(self):
        if self._description:
            return '<Phase {name} ({description}): {energy}>'.format(
                    name=self.name, energy=self.energy, description=self._description)
        else:
            return '<Phase {name} : {energy}>'.format(
                    name=self.name, energy=self.energy)

    def __eq__(self,other):
        """
        Phases are defined to be equal if they have the same composition and an
        energy within 1e-6 eV/atom.
        """
        if set(self.comp) != set(other.comp):
            return False
        if abs(self.energy - other.energy) > 1e-6:
           return False
        for key in self.comp:
           if abs(self.unit_comp[key]-other.unit_comp[key]) > 1e-6:
                return False
        return True

    @property
    def label(self):
        return '%s: %0.3f eV/atom' % (self.name, self.energy)

    @property
    def link(self):
        if self.id:
            link = '<a href="/materials/entry/{id}">{name}</a>'
            return link.format(id=self.calculation.entry_id, name=self.name)
        else:
            return ''

    @property
    def name(self):
        if self.custom_name:
            return self.custom_name
        if self.phase_dict:
            name_dict = dict((p, v/p.natoms) for p, v in
                    self.phase_dict.items())
            return ' + '.join('%.3g %s' % (v, p.name) for p, v in name_dict.items())
        return format_comp(self.nom_comp)

    @property
    def latex(self):
        if self.phase_dict:
            return ' + '.join('%.3g %s' % (v, p.latex) for p, v in
                    self.phase_dict.items())
        return format_latex(self.nom_comp)

    @property
    def volume(self):
        if self.phase_dict:
            return sum( phase.calculation.volume_pa*amt for phase, amt in
                    self.phase_dict.items() )
        else:
            return self.calculation.volume_pa

    @property
    def mass(self):
        if self.phase_dict:
            return sum( phase.calculation.composition.get_mass()*amt for phase, amt in
                    self.phase_dict.items() )
        else:
            return self.calculation.composition.get_mass()

    @property
    def space(self):
        """
        Set of elements in the phase.
        """
        return set([ k for k, v in self.unit_comp.items() 
            if abs(v) > 1e-6 ])

    @property
    def n(self):
        """
        Number of atoms in the total composition.
        """
        return sum(self._comp.values())

    @property
    def comp(self):
        """
        Total composition.
        """
        return self._comp

    @property
    def unit_comp(self):
        """
        Unit composition.
        """
        return unit_comp(self.comp)

    @property
    def nom_comp(self):
        """
        Composition divided by the GCD. e.g. Fe4O6 becomes Fe2O3.
        """
        return reduce_comp(self.comp)

    @property
    def description(self):
        """
        Some description of the phase origin.
        """
        return self._description

    @property
    def energy(self):
        """
        Energy per atom in eV.
        """
        return self._energy

    @property
    def total_energy(self):
        """
        Total energy for the composition as supplied (in eV).
        """
        return self._total_energy

    @property
    def energy_pfu(self):
        """
        Energy per nominal composition. i.e. energy per Fe2O3, not Fe4O6.
        """
        return self._energy_pfu

    _gap = None
    @property
    def band_gap(self):
        if not self._gap:
            self.get_gap()
        return self._gap

    def get_gap(self):
        if not self.phase_dict:
            self._gap = self.calculation.band_gap
        else:
            self._gap = min([ p.calculation.band_gap for p in
                self.phase_dict ])

    _formation = None
    @property
    def formation(self):
        if self.id is None:
            return
        if self._formation is None:
            self._formation = qmpy.FormationEnergy.objects.get(id=self.id)
        return self._formation

    @property
    def calculation(self):
        """
        Get the oqmd Formation object for this Phase, if it exists.
        """
        if self.id is None:
            return
        from qmpy.analysis.vasp.calculation import Calculation
        return self.formation.calculation

    def set_stability(self):
        from qmpy.analysis.vasp import Calculation
        if self.id is None:
            return
        Calculation.objects.filter(id=self.id).update(stability=self.stability)

    def free_energy(self, T=0, P=0, mus={}):
        """
        Free energy function for the phase, can be defined to be anything, by
        default it just returns the phase's ground state energy.
        """
        #global environment
        return self._energy

    def fraction(self, comp):
        """
        Returns a composition dictionary with the specified composition pulled
        out as 'var'. 

        Example:
        >>> phase = Phase(composition={'Fe':1, 'Li':5, 'O'8'}, energy=-1)
        >>> phase.fraction('Li2O')
        defaultdict(<type 'float'>, {'var': 2.5, 'Fe': 1, 'O': 5.5, 'Li': 0.0})
        """
        if isinstance(comp, Phase):
            comp = comp.unit_comp
        elif isinstance(comp, basestring):
            comp = unit_comp(parse_comp(comp))
        residual = defaultdict(float, self.unit_comp)
        tot = sum(residual.values())
        for c, amt in dict(comp).items():
            pres = residual[c]/amt
            for c2, amt2 in comp.items():
                residual[c2] -= pres*amt2
        residual['var'] = (tot - sum(residual.values()))
        residual['var'] /= float(sum(comp.values()))
        return residual
