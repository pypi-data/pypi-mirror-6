# qmpy/analysis/vasp/calculation.py

"""
The Calculation class is the container for all information about a calculation,
and is used to read/write/create calculation directories.

"""

import os
import copy
import json
import time
import gzip
import numpy as np
import numpy.linalg
import logging
import re
import subprocess
from collections import defaultdict
from os.path import exists, isfile, isdir

try:
    from lxml import etree
except ImportError:
    import elementtree.ElementTree as etree

from django.db import models
from django.db import transaction

import qmpy
import qmpy.materials.composition as comp
import qmpy.materials.structure as strx
import qmpy.io.poscar as poscar
import potential as pot
import qmpy.materials.formation_energy as fe
import qmpy.utils as utils
import qmpy.db.custom as cdb
import qmpy.analysis.thermodynamics as thermo
import qmpy.analysis.griddata as grid
import dos
from qmpy.data import chem_pots
from qmpy.materials.atom import Atom, Site
from qmpy.utils import *
from qmpy.data.meta_data import MetaData, add_meta_data
from qmpy.materials.element import Element
from qmpy.db.custom import DictField, NumpyArrayField
from qmpy.configuration.vasp_settings import *

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

re_iter = re.compile('([0-9]+)\( *([0-9]+)\)')

def value_formatter(value):
    if isinstance(value, list):
        return ' '.join(map(value_formatter, value))
    elif isinstance(value, basestring):
        return value.upper()
    elif isinstance(value, bool):
        return ('.%s.' % value).upper()
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return '%0.8g' % value
    else:
        return str(value)

def vasp_format(key, value):
    return ' %s = %s' % (key.upper(), value_formatter(value))

class VaspError(Exception):
    """General problem with vasp calculation."""

@add_meta_data('error')
@add_meta_data('warning')
class Calculation(models.Model):
    """
    Base class for storing a VASP calculation.

    Relationships:
        | :mod:`~qmpy.Composition` via composition
        | :mod:`~qmpy.DOS` via dos
        | :mod:`~qmpy.Structure` via input. Input structure.
        | :mod:`~qmpy.Structure` via output. Resulting structure.
        | :mod:`~qmpy.Element` via element_set.
        | :mod:`~qmpy.Potential` via potential_set.
        | :mod:`~qmpy.Hubbard` via hubbard_set.
        | :mod:`~qmpy.Entry` via entry.
        | :mod:`~qmpy.Fit` via fit. Reference energy sets that have been fit using
        |   this calculation.
        | :mod:`~qmpy.FormationEnergy` via formationenergy_set. Formation
        |   energies computed from this calculation, for different choices of
        |   fit sets.
        | :mod:`~qmpy.MetaData` via meta_data

    Attributes:
        | id
        | label: key for entry.calculations dict.
        | attempt: # of this attempt at a calculation.
        | band_gap: Energy gap occupied by the fermi energy.
        | configuration: Type of calculation (module).
        | converged: Did the calculation converge electronically and ionically.
        | energy: Total energy (eV/UC)
        | energy_pa: Energy per atom (eV/atom)
        | irreducible_kpoints: # of irreducible k-points.
        | magmom: Total magnetic moment (mu_b)
        | magmom_pa: Magnetic moment per atom. (mu_b/atom)
        | natoms: # of atoms in the input.
        | nsteps: # of ionic steps.
        | path: Calculation path.
        | runtime: Runtime in seconds.
        | settings: dictionary of VASP settings.

    """
    #= labeling =#
    configuration = models.CharField(db_index=True, max_length=15, 
            null=True, blank=True)
    meta_data = models.ManyToManyField(MetaData)

    label = models.CharField(max_length=63, default='')
    entry = models.ForeignKey('Entry', db_index=True, null=True, blank=True)
    path = models.CharField(max_length=255, null=True, db_index=True)

    composition = models.ForeignKey('Composition', null=True, blank=True)
    element_set = models.ManyToManyField('Element')
    natoms = models.IntegerField(blank=True, null=True)

    #= inputs =#
    input = models.ForeignKey(strx.Structure, 
                              related_name='calculated',
                              null=True, blank=True)
    hubbard_set = models.ManyToManyField('Hubbard')
    potential_set = models.ManyToManyField('Potential')
    settings = DictField(blank=True, null=True)
    
    #= outputs =#
    output = models.ForeignKey(strx.Structure, 
                               related_name='source',
                               null=True, blank=True)

    energy = models.FloatField(null=True, blank=True)
    energy_pa = models.FloatField(null=True, blank=True)
    magmom = models.FloatField(blank=True, null=True)
    magmom_pa = models.FloatField(blank=True, null=True)
    dos = models.ForeignKey('DOS', blank=True, null=True)
    band_gap = models.FloatField(blank=True, null=True)
    irreducible_kpoints = models.FloatField(blank=True, null=True)

    #= progress/completion =#
    attempt = models.IntegerField(default=0, blank=True, null=True)
    nsteps = models.IntegerField(blank=True, null=True)
    converged = models.NullBooleanField(null=True)
    runtime = models.FloatField(blank=True, null=True)

    #= Non-stored values =#
    outcar = None
    kpoints = None
    occupations = None
    formation = None

    class Meta:
        app_label = 'qmpy'
        db_table = 'calculations'

    # builtins
    def __str__(self):
        retval = ''
        if self.input:
            retval += self.input.name+' @ '
        if self.configuration:
            retval += self.configuration+' settings'
        elif 'prec' in self.settings:
            retval += 'PREC='+self.settings['prec'].upper()
        if self.settings.get('nsw', 1) <= 1:
            retval += ', static'
        if not retval:
            return 'Blank'
        return retval

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.output is not None:
            if self.entry:
                self.output.entry = self.entry
            self.output.save()
            self.output = self.output
            self.composition = self.output.composition
        if self.input is not None:
            if self.entry:
                self.input.entry = self.entry
            self.input.save()
            self.input = self.input
            self.composition = self.input.composition
        if self.dos is not None:
            self.dos.entry = self.entry
            self.dos.save()
            self.dos = self.dos
        super(Calculation, self).save(*args, **kwargs)
        self.hubbard_set = self.hubbards
        self.potential_set = self.potentials
        self.element_set = self.elements
        self.meta_data = self.error_objects
        if self.formation:
            self.formationenergy_set.add(self.formation)

    # django caching
    _potentials = None
    @property
    def potentials(self):
        if self._potentials is None:
            if not self.id:
                self._potentials = []
            else:
                self._potentials = list(self.potential_set.all())
        return self._potentials

    @potentials.setter
    def potentials(self, potentials):
        self._potentials = potentials

    _elements = None
    @property
    def elements(self):
        if self._elements is None:
            if self.id:
                self._elements = list(self.element_set.all())
            else:
                self._elements = list(set([ a.element for a in self.input ]))
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = elements

    _hubbards = None
    @property
    def hubbards(self):
        if self._hubbards is None:
            if not self.id:
                self._hubbards = []
            else:
                self._hubbards = list(self.hubbard_set.all())
        return self._hubbards

    @hubbards.setter
    def hubbards(self, hubbards):
        self._hubbards = hubbards

    # accessors/aggregators
    @property
    def comp(self):
        return self.output.comp

    @property
    def hub_comp(self):
        hcomp = defaultdict(int)
        for h in self.hubbards:
            if not h:
                continue
            for a in self.input:
                if ( h.element == a.element and
                        h.ox in [None, a.ox]):
                    hcomp[h] += 1
        return dict(hcomp.items())

    @property
    def true_comp(self):
        comp = defaultdict(int)
        for c, v in self.comp.items():
            if self.hubbard_set.filter(element=c).exists():
                h = self.hubbard_set.get(element=c)
                if h:
                    comp['%s_%s' % (c, h.u)] += v
                    continue
            comp[c] += v
        return dict(comp)

    @property
    def unit_comp(self):
        return unit_comp(self.comp)

    @property
    def needs_hubbard(self):
        return any( h for h in self.hubbards )

    #= input files as strings =#
    @property
    def POSCAR(self):
        return poscar.write(self.input)

    @property
    def INCAR(self):
        return self.get_incar()

    @property
    def KPOINTS(self):
        return self.get_kpoints()

    @property
    def POTCAR(self):
        return self.get_potcar()

    # INCAR / settings
    @property
    def MAGMOMS(self):
        moments = [ a.magmom for a in self.input.atoms ]
        if all([ m in [0, None] for m in moments ]):
            return ''
        magmoms = [[ 1, moments[0]]]
        for n in range(1, len(moments)):
            if moments[n] == moments[n-1]:
                magmoms[-1][0] += 1
            else:
                magmoms.append([1, moments[n]])
        momstr = ' '.join('%i*%.4f' % (v[0],v[1]) for v in magmoms)
        return '  MAGMOM = %s' % momstr

    @property
    def phase(self):
        p = thermo.Phase(energy=self.delta_e,
                composition=parse_comp(self.composition_id),
                description=str(self.input.spacegroup),
                stability=self.stability,
                per_atom=True)
        p.id = self.id
        return p

    def calculate_stability(self, fit='standard'):
        from qmpy.analysis.thermodynamics import PhaseSpace
        ps = PhaseSpace(self.input.comp)
        ps.compute_stabilities()

    def get_incar(self):
        s = dict((k.lower(), v) for k, v in self.settings.items() if not k in
                ['gamma', 'kppra', 'scale_encut', 'potentials', 'hubbards'])

        incar = '#= General Settings =#\n'
        for key in ['prec', 'istart', 'icharg', 'lsorbit', 'nelect']:
            if key in s:
                incar += ' %s\n' % vasp_format(key, s.pop(key))

        if self.MAGMOMS and not 'ispin' in s:
            s['ispin'] = 2
        incar += '  ISPIN = %d\n' % s.pop('ispin', 1)
        if self.MAGMOMS:
            incar += self.MAGMOMS+'\n'

        if  any(hub for hub in self.hubbards):
            incar += '\n#= LDA+U Fields =#\n'
            incar += ' LDAU = .TRUE.\n'
            incar += ' LDAUPRINT = 1\n'
            hubbards = sorted(self.hubbards, key=lambda x: x.element_id)
            uvals = ' '.join(str(hub.u) for hub in hubbards)
            jvals = ' '.join('0' for hub in hubbards)
            lvals = ' '.join(str(hub.l) for hub in hubbards)
            incar += ' LDAUU = %s\n' % uvals
            incar += ' LDAUJ = %s\n' % jvals
            incar += ' LDAUL = %s\n' % lvals

        incar += '\n#= Parallelization =#\n'
        for key in ['lplane', 'nsim', 'ncore', 'lscalu', 'npar']:
            if key in s:
                incar += ' %s\n' % vasp_format(key, s.pop(key))

        incar += '\n#= Ionic Relaxation Settings =#\n'
        for key in ['nsw', 'ibrion', 'isif', 'isym', 
                    'symprec', 'potim', 'ediffg']:
            if key in s:
                incar += ' %s\n' % vasp_format(key, s.pop(key))

        incar += '\n#= Electronic Relxation Settings =#\n'
        for key in ['encut', 'nelm', 'nelmin', 'lreal', 'ediff', 'algo']:
            if key in s:
                incar += ' %s\n' % vasp_format(key, s.pop(key))

        incar += '\n#= Write flags =#\n'
        for key in ['lcharg', 'lwave', 'lelf', 'lhvar', 'lvtot']:
            if key in s:
                incar += ' %s\n' % vasp_format(key, s.pop(key))

        incar += '\n#= DOS =#\n'
        for key in ['nbands', 'ismear', 'sigma']:
            if key in s:
                incar += ' %s\n' % vasp_format(key, s.pop(key))

        if s.get('ldipol', False):
            incar += '\n# dipole fields\n'
            incar += ' LDIPOL = .TRUE.\n'
            for k in ['idipol', 'espilon']:
                if k in s:
                    incar += ' %s\n' % vasp_format(k, s.pop(k))

        incar += '\n#= Uncategorized/OQMD codes  =#\n'
        for k, v in s.items():
            incar += ' %s\n' % (vasp_format(k, v))
        return incar

    @INCAR.setter
    def INCAR(self, incar):
        settings = {}
        custom = ''
        magmoms = []
        ldauus = []
        ldauls = []
        ldaujs = []
        for line in open(incar):
            line = line.lower()
            line = line.split('=')
            settings[line[0].strip()] = line[1].strip()

        if self.input is not None:
            atom_types = []
            for atom in self.input.atoms:
                if atom.element.symbol in atom_types:
                    continue
                atom_types.append(atom.element.symbol)
            if ldauus and ldauls:
                assert len(ldauls) == len(atom_types)
                assert len(ldauus) == len(atom_types)
                for elt, u, l in zip(atom_types, ldauus, ldauls):
                    hub, created = pot.Hubbard.objects.get_or_create(element_id=elt,
                            u=u, l=l)
                    self.hubbards.append(hub)
            if magmoms:
                real_moms = []
                for mom in magmoms:
                    if '*' in mom:
                        num, mom = mom.split('*')
                        real_moms += [mom]*int(num)
                    else:
                        real_moms.append(mom)
                for atom, mom in zip(self.input.atoms, real_moms):
                    atom.magmom = float(mom)
                    if atom.id is not None:
                        atom.save()
        self.settings = settings

    def get_kpoints(self):
        kpts = self.input.get_kpoint_mesh(self.settings.get('kppra', 8000))
        if self.settings.get('gamma', True):
            kpoints = 'KPOINTS \n0 \nGamma\n'
        else:
            kpoints = 'KPOINTS \n0 \nMonkhost-Pack\n'
        kpoints += ' '.join( str(int(k)) for k in kpts ) + '\n'
        kpoints += '0 0 0'
        return kpoints

    @KPOINTS.setter
    def KPOINTS(self, kpoints):
        raise NotImplementedError

    def get_potcar(self, distinct_by_ox=False):
        potstr = ''
        if not distinct_by_ox:
            elts = sorted(self.input.comp.keys())
        else:
            e_o_pairs = set([ (a.element_id, a.ox)
                for a in self.input ])
            elts = sorted([ p[0] for p in e_o_pairs ])

        for elt in elts:
            pot = [ p for p in self.potentials if p.element_id == elt ][0]
            potstr += pot.potcar
            potstr += ' End of Dataset\n'
        return potstr

    @POTCAR.setter
    def POTCAR(self, potcar):
        pots = pot.Potential.read_potcar(potcar)
        for pot in pots:
            self.potentials.append(pot)

    @POSCAR.setter
    def POSCAR(self, poscar):
        self.input = poscar.read(poscar)

    xmlroot = None
    def read_vasprun_xml(self):
        tree = etree.parse(gzip.open(self.path+'/vasprun.xml.gz','rb'))
        self.xmlroot = tree.getroot()

        # read settings
        settings = {}
        for s in self.xmlroot.findall('parameters/separator/*'):
            t = s.get('type', 'float')
            if not s.text:
                continue
            if s.tag == 'i':
                if t == 'int':
                    settings[s.get('name').lower()] = int(s.text.strip())
                elif t == 'float':
                    settings[s.get('name').lower()] = float(s.text.strip())
                elif t == 'string':
                    settings[s.get('name').lower()] = s.text.strip()
            elif s.tag == 'v':
                settings[s.get('name').lower()] = map(float, s.text.split())
        self.settings = settings

        # read other things
        lattices = []
        for b in self.xmlroot.findall("structure/crystal/*[@name='basis']"):
            cell = []
            for v in b:
                cell.append(map(float, v.strip().split()))
            lattices.append(np.vstack(cell))

        # coords
        positions = []
        for c in self.xmlroot.findall("structure/varray[@name='positions']"):
            coords = []
            for v in c:
                coords.append(map(float, v.strip().split()))
            positions.append(np.vstack(coords))

        raise NotImplementedError
        # energies
        energies = []

        # forces
        forces = []

        # stresses
        stresses = []

    def get_outcar(self):
        """
        Sets the calculations outcar attribute to a list of lines from the
        outcar. 

        Examples::

            >>> calc = Calculation.read('calculation_path')
            >>> print calc.outcar
            None
            >>> calc.get_outcar()
            >>> len(calc.outcar)
            12345L
        
        """
        if not self.outcar is None:
            return self.outcar
        if not exists(self.path):
            return
        elif exists(self.path+'/OUTCAR'):
            self.outcar = open(self.path+'/OUTCAR').read().split('\n')
        elif exists(self.path+'/OUTCAR.gz'):
            self.outcar = gzip.open(self.path + '/OUTCAR.gz', 'rb').read().split('\n')
        else:
            raise VaspError('No such file exists')

    def read_runtime(self):
        self.get_outcar()
        runtime = 0
        for line in self.outcar:
            if 'LOOP+' in line:
                if not len(line.split()) == 7:
                    continue
                runtime += ffloat(line.split()[-1])
        self.runtime = runtime
        return runtime

    def read_energies(self):
        """
        Returns a numpy.ndarray of energies over all ionic steps.

        Examples::

            >>> calc = Calculation.read('calculation_path')
            >>> calc.read_energies()
            array([-12.415236, -12.416596, -12.416927])
        
        """        
        self.get_outcar()
        energies = []
        for line in self.outcar:
            if 'free  energy' in line:
                energies.append(ffloat(line.split()[4]))
        self.energies = np.array(energies)
        return self.energies

    def read_natoms(self):
        """Reads the number of atoms, and assigns the value to natoms."""
        self.get_outcar()
        for line in self.outcar:
            if 'NIONS' in line:
                self.natoms = int(line.split()[-1])
                return self.natoms

    def read_n_ionic(self):
        """Reads the number of ionic steps, and assigns the value to nsteps."""
        self.get_outcar()
        self.nsteps = len([ l for l in self.outcar if 'free  energy' in l ])
        return self.nsteps

    def read_input_structure(self):
        if os.path.exists(self.path+'/POSCAR'):
            self.input = poscar.read(self.path+'/POSCAR')
            self.input.entry = self.entry

    def read_elements(self):
        """
        Reads the elements of the atoms in the structure. Returned as a list of
        atoms of shape (natoms,). 

        Examples::

            >>> calc = Calculation.read('path_to_calculation')
            >>> calc.read_elements()
            ['Fe', 'Fe', 'O', 'O', 'O']

        """
        self.get_outcar()
        elt_list = []
        elements = []
        for line in self.outcar:
            if 'POTCAR:' in line:
                elt = line.split()[2].split('_')[0]
                elt_list.append(elt)
            if 'ions per type' in line:
                elt_list = elt_list[:len(elt_list)/2]
                self.elements = [ Element.get(e) for e in elt_list ]
                counts = map(int, line.split()[4:])
                assert len(counts) == len(elt_list)
                for n, e in zip(counts, elt_list):
                    elements += [e]*n
                break
        self.elements = elements
        return self.elements

    def read_lattice_vectors(self):
        """
        Reads and returns a numpy ndarray of lattice vectors for every ionic 
        step of the calculation.

        Examples::

            >>> path = 'analysis/vasp/files/magnetic/standard'
            >>> calc = Calculation.read(INSTALL_PATH+'/'+path)
            >>> calc.read_lattice_vectors()
            array([[[ 5.707918,  0.      ,  0.      ],
                    [ 0.      ,  5.707918,  0.      ],
                    [ 0.      ,  0.      ,  7.408951]],
                   [[ 5.707918,  0.      ,  0.      ],
                    [ 0.      ,  5.707918,  0.      ],
                    [ 0.      ,  0.      ,  7.408951]]])

        """
        self.get_outcar()
        lattice_vectors = []
        for i, line in enumerate(self.outcar):
            if 'direct lattice vectors' in line:
                tlv = []
                for n in range(3):
                    tlv.append(read_fortran_array(self.outcar[i+n+1], 6)[:3])
                lattice_vectors.append(tlv)
        return np.array(lattice_vectors)

    def read_charges(self):
        """
        Reads and returns VASP's calculated charges for each atom. Returns the
        RAW charge, not NET charge.
        
        Examples::

            >>> calc = Calculation.read('path_to_calculation')
            >>> calc.read_charges()

        """
        self.get_outcar()
        self.read_natoms()
        self.read_n_ionic()
        self.read_runtime()
        if self.settings is None:
            self.read_outcar_settings()
        if not self.settings['lorbit'] == 11:
            return np.array([[0]*self.natoms]*self.nsteps)

        charges = []
        for n, line in enumerate(self.outcar):
            if 'total charge ' in line:
                chgs = []
                for i in range(self.natoms):
                    chgs.append(float(self.outcar[n+4+i].split()[-1]))
                charges.append(chgs)
        return np.array(charges)

    def read_magmoms(self):
        self.get_outcar()
        self.read_natoms()
        self.read_n_ionic()
        if self.settings is None:
            self.read_outcar_settings()
        if self.settings['ispin'] == 1:
            return np.array([[0]*self.natoms]*self.nsteps)

        magmoms = []
        for n, line in enumerate(self.outcar):
            if 'magnetization (x)' in line:
                mags = []
                for i in range(self.natoms):
                    mags.append(float(self.outcar[n+4+i].split()[-1]))
                magmoms.append(mags)
            if 'number of electron' in line:
                if 'magnetization' in line:
                    self.magmom = float(line.split()[-1])
        if self.settings['lorbit'] != 11:
            return np.array([[0]*self.natoms]*self.nsteps)
        return magmoms

    def read_forces(self):
        self.get_outcar()
        self.read_natoms()
        forces = []
        force_loop = [None]*self.natoms
        for line in self.outcar:
            if 'POSITION' in line:
                force_loop = []
            elif len(force_loop) < self.natoms:
                if '------' in line:
                    continue
                force_loop.append(map(float, line.split()[3:]))
                if len(force_loop) == self.natoms:
                    forces.append(force_loop)
        return np.array(forces)

    def read_positions(self):
        self.get_outcar()
        self.read_natoms()
        positions = []
        position_loop = [None]*self.natoms
        for line in self.outcar:
            if 'POSITION' in line:
                position_loop = []
            elif len(position_loop) < self.natoms:
                if '------' in line:
                    continue
                position_loop.append(map(float, line.split()[:3]))
                if len(position_loop) == self.natoms:
                    positions.append(position_loop)
        return np.array(positions)

    def read_stresses(self):
        self.get_outcar()
        stresses = []
        check = False
        for line in self.outcar:
            if 'FORCE on cell' in line:
                check = True
            if check and 'Total' in line:
                stresses.append(map(ffloat, line.split()[1:]))
                check = False
        return np.array(stresses)

    def read_kpoints(self):
        kpts = []
        weights = []
        found = False
        for i, line in enumerate(self.outcar):
            if 'irreducible k-points' in line:
                self.irreducible_kpoints = int(line.split()[1])
            if 'k-points in reciprocal lattice and weights' in line:
                for j in range(self.irreducible_kpoints):
                    x,y,z,w = map(float, self.outcar[i+j+1].split())
                    kpts.append([x,y,z])
                    weights.append(w)
                else:
                    break
        self.kpoints = kpts
        self.kpt_weights = weights

    def read_occupations(self):
        if self.kpoints is None:
            self.read_kpoints()
        if self.settings is None:
            self.read_outcar_settings()
        occs = []
        bands = []
        for i, line in enumerate(self.outcar):
            if 'k-point' in line:
                if not 'occupation' in self.outcar[i+1]:
                    continue
                if ' 1 ' in line:
                    occs = []
                    bands = []
                tocc = []
                tband = []
                for j in range(self.settings['nbands']):
                    b, e, o = map(ffloat, self.outcar[i+j+2].split())
                    tocc.append(o)
                    tband.append(e)
                occs.append(tocc)
                bands.append(tband)
        self.occupations = np.array(occs)
        self.bands = np.array(bands)

    def read_outcar_results(self):
        self.read_natoms()
        self.read_convergence()
        elts = self.read_elements()
        energies = self.read_energies()
        lattice_vectors = self.read_lattice_vectors()
        stresses = self.read_stresses()
        positions = self.read_positions()
        forces = self.read_forces()
        magmoms = self.read_magmoms()
        charges = self.read_charges()

        if len(self.energies) > 0:
            self.energy = self.energies[-1]
            self.energy_pa = self.energy/self.natoms
        if not self.magmom is None:
            self.magmom_pa = self.magmom/self.natoms

        if self.nsteps > 0:
            output = strx.Structure()
            output.total_energy = energies[-1]
            output.cell = lattice_vectors[-1]
            output.stresses = stresses[-1]
            inv = numpy.linalg.inv(output.cell).T
            atoms = []
            for coord, forces, charge, magmom, elt in zip(positions[-1], 
                                                          forces[-1],
                                                          charges[-1],
                                                          magmoms[-1],
                                                          elts):
                a = Atom(element_id=elt, charge=charge, magmom=magmom)
                a.coord = np.dot(inv, coord)
                a.forces = forces
                atoms.append(a)
            output.atoms = atoms
            self.output = output
            self.output.set_label(self.label)

    def read_convergence(self):
        self.get_outcar()
        if not self.settings:
            self.read_outcar_settings()
        check_ionic = False
        if self.settings.get('nsw', 1) > 1:
            check_ionic = True

        v_init = None
        for line in self.outcar:
            if 'volume of cell' in line:
                v_init = float(line.split(':')[1].strip())
                break

        sc_converged, forces_converged = False, False
        v_fin = None
        for line in self.outcar[::-1]:
            if 'Iteration' in line:
                ionic, electronic = map(int, re_iter.findall(line)[0])
                if self.settings.get('nelm', 60) == electronic:
                    sc_converged = False
                if self.settings.get('nsw', 0) == ionic:
                    forces_converged = False
                break
            if 'EDIFF is reached' in line:
                sc_converged = True
            if 'reached required accuracy' in line:
                forces_converged = True
            if 'volume of cell' in line:
                v_fin = float(line.split(':')[1].strip())

        if v_fin is None or v_init is None:
            basis_converged = False
        else:
            basis_converged = ( abs(v_fin - v_init)/v_init < 0.05 )

        if self.configuration in ['initialize', 
                                  'coarse_relax', 
                                  'fine_relax',
                                  'standard']:
            basis_converged = True

        if (sc_converged and 
                ((forces_converged and check_ionic) or not check_ionic) and
                basis_converged):
            self.converged = True
        else:
            self.add_error('convergence')
            self.converged = False

    def read_outcar_settings(self):
        self.get_outcar()
        settings = {'potentials':[]}
        elts = []
        for line in self.outcar:
            ### general options
            if 'PREC' in line:
                settings['prec'] = line.split()[2]
            elif 'ENCUT' in line:
                settings['encut'] = float(line.split()[2])
            elif 'ISTART' in line:
                settings['istart'] = int(line.split()[2])
            elif 'ISPIN' in line:
                settings['ispin'] = int(line.split()[2])
            elif 'ICHARG' in line:
                settings['icharg'] = int(line.split()[2])

            # electronic relaxation 1
            elif 'NELM' in line:
                settings['nelm'] = int(line.split()[2].rstrip(';'))
                settings['nelmin'] = int(line.split()[4].rstrip(';'))
            elif 'LREAL  =' in line:
                lreal = line.split()[2]
                if lreal == 'F':
                    settings['lreal'] = False
                elif lreal == 'A':
                    settings['lreal'] = 'auto'
                elif lreal == 'T':
                    settings['lreal'] = True

            # ionic relaxation 
            elif 'EDIFF  =' in line:
                settings['ediff'] = float(line.split()[2])
            elif 'ISIF' in line:
                settings['isif'] = int(line.split()[2])
            elif 'IBRION' in line:
                settings['ibrion'] = int(line.split()[2])
            elif 'NSW' in line:
                settings['nsw'] = int(line.split()[2].rstrip(';'))
            elif 'PSTRESS' in line:
                settings['pstress'] = float(line.split()[1])
            elif 'POTIM' in line:
                settings['potim'] = float(line.split()[2])

            # DOS Flags
            elif 'ISMEAR' in line:
                line = line.split()
                settings['ismear'] = int(line[2].rstrip(';'))
                settings['sigma'] = float(line[5])
            elif 'NBANDS=' in line:
                if not 'INCAR' in line:
                    settings['nbands'] = int(line.split()[-1])

            # write flags
            elif 'LCHARG' in line:
                settings['lcharg'] = ( line.split()[2] != 'F' )
            elif 'LWAVE' in line:
                settings['lwave'] = ( line.split()[2] == 'T' )
            elif 'LVTOT' in line:
                settings['lvtot'] = ( line.split()[2] == 'T' )
            elif 'LORBIT' in line:
                settings['lorbit'] = int(line.split()[2])

            # electronic relaxation 2
            elif 'ALGO' in line:
                algo_dict = {38:'normal',
                             68:'fast',
                             48:'very_fast',
                             58:'all',
                             53:'default'}
                settings['algo'] = algo_dict[int(line.split()[2])]

            # dipole flags
            elif 'LDIPOL' in line:
                settings['ldipol'] = ( line.split()[2] == 'T')
            elif 'IDIPOL' in line:
                settings['idipol'] = int(line.split()[2])
            elif ' EPSILON=' in line:
                settings['epsilon'] = float(line.split()[1])
            
            # potentials
            elif 'POTCAR:' in line:
                this_pot = {'name':line.split()[2]}
            elif 'Description' in line:
                settings['potentials'].append(this_pot)
            elif 'LEXCH' in line:
                key = line.split()[2]
                if key == '91':
                    this_pot['xc'] = 'GGA'
                elif key == 'CA':
                    this_pot['xc'] = 'LDA'
                elif key == 'PE':
                    this_pot['xc'] = 'PBE'
            elif 'LULTRA' in line:
                key = line.split()[2]
                this_pot['us'] = ( key == 'T' )
            elif 'LPAW' in line:
                key = line.split()[2]
                this_pot['paw'] = ( key == 'T' )
            # hubbards
            elif 'LDAUL' in line:
                settings['ldau'] = True
                settings['ldauls'] = [ int(v) for v in line.split()[7:] ]
            elif 'LDAUU' in line:
                settings['ldauus'] = [ float(v) for v in line.split()[7:] ]
            elif 'energy-cutoff' in line:
                break

        # assign potentials
        xcs = list(set([ p['xc'] for p in settings['potentials']]))
        uss = list(set([ p['us'] for p in settings['potentials']]))
        paws = list(set([ p['paw'] for p in settings['potentials']]))
        pot_names = [ p['name'] for p in settings['potentials']]
        elts = [ p['name'].split('_')[0] for p in settings['potentials'] ]
        if any([ len(s) > 1 for s in [xcs, uss, paws]]):
            raise VaspError('Not all potentials are of the same type')
        self.potentials = pot.Potential.objects.filter(us=uss[0], 
                                              xc=xcs[0], 
                                              paw=paws[0],
                                              name__in=pot_names)

        # assign hubbards
        self.hubbards = []
        if 'ldauls' in settings:
            for elt, l, u in zip(elts, 
                                 settings['ldauls'], 
                                 settings['ldauus']):
                self.hubbards.append(pot.Hubbard.get(elt, u=u, l=l))
        self.settings = settings

    def read_stdout(self, filename='stdout.txt'):
        if not os.path.exists('%s/%s' % (self.path, filename)):
            return []
        stdout = open('%s/%s' % (self.path, filename)).read()
        errors = []
        if 'Error reading item' in stdout:
            self.add_error('input_error')
        if 'ZPOTRF' in stdout:
            self.add_error('zpotrf')
        if 'SGRCON' in stdout:
            self.add_error('sgrcon')
        if 'INVGRP' in stdout:
            self.add_error('invgrp')
        if 'BRIONS problems: POTIM should be increased' in stdout:
            self.add_error('brions')
        if 'TOO FEW BANDS' in stdout:
            self.add_error('bands')
        if 'FEXCF' in stdout:
            self.add_error('fexcf')
        if 'FEXCP' in stdout:
            self.add_error('fexcp')
        if 'PRICEL' in stdout:
            self.add_error('pricel')
        if 'EDDDAV' in stdout:
            self.add_error('edddav')
        if 'Sub-Space-Matrix is not hermitian in DAV' in stdout:
            self.add_error('hermitian')
        if 'IBZKPT' in stdout:
            self.add_warning('IBZKPT error')
        if 'BRMIX: very serious problems' in stdout:
            self.add_error('brmix')
        return self.errors

    def read_outcar_started(self):
        self.get_outcar()
        if len(self.outcar) < 5:
            return False
        found_inputs = [False, False, False, False]
        for line in self.outcar:
            if 'INCAR:' in line:
                found_inputs[0] = True
            if 'POTCAR:' in line: 
                found_inputs[1] = True
            if 'KPOINTS:' in line:
                found_inputs[2] = True
            if 'POSCAR:' in line:
                found_inputs[3] = True
            if all(found_inputs):
                break
        if not all(found_inputs):
            return False
        return True

    def read_outcar(self):
        self.get_outcar()
        if not self.read_outcar_started():
            return
        if self.input is None:
            self.read_input_structure()
        self.read_outcar_settings()
        self.read_outcar_results()
        self.read_n_ionic()

    def read_chgcar(self, filename='CHGCAR.gz', filetype='CHGCAR'):
        """
        Reads a VASP CHGCAR or ELFCAR and returns a GridData instance.

        """

        # Determine the number of data columns
        if 'CHGCAR' in filename:
            width = 5
        elif 'ELFCAR' in filename:
            width = 10
        else:
            width = 5
        
        if not os.path.exists(self.path+'/'+filename):
            raise VaspError("%s does not exist at %s", filetype, filename)

        if '.gz' in filename:
            f = gzip.open('%s/%s' % (self.path,filename),'rb')
        else:
            f = open('%s/%s' % (self.path,filename),'r')

        d = f.readlines() 
        lattice = np.array([map(float, r.split()) for r in d[2:5]])
        stoich = np.array(d[6].split(),int)
        count = sum(stoich)
        meshsize = np.array(d[9+int(count)].split(),int)
        mesh_spacing = 1./meshsize
        top = 10+int(count)
        length = int(np.floor(np.product(meshsize)/width))
        list = np.array(map(lambda d:
            np.array(d.strip().split(), float), d[top:top+length]))
        if np.product(meshsize) % width != 0:
            trail = d[top+length].rstrip().split()
            rem = np.product(meshsize) % width
            list = np.append(list, np.array(trail[0:rem],float))

        new_list = np.reshape(list, meshsize[::-1])
        self.xdens = grid.GridData(new_list.swapaxes(0,2),
                lattice=lattice)
        return self.xdens

    def read_doscar(self):
        if os.path.getsize(self.path+'/DOSCAR') < 300:
            return
        self.dos = dos.DOS.read(self.path+'/DOSCAR')
        self.band_gap = self.dos.find_gap()
        return self.dos

    def clear_outputs(self):
        if not os.path.exists(self.path):
            return
        for file in os.listdir(self.path):
            if os.path.isdir(self.path+'/'+file):
                continue
            if file in ['INCAR', 'POSCAR', 'KPOINTS', 'POTCAR']:
                continue
            os.unlink('%s/%s' % (self.path, file))

    def clear_results(self):
        self.energy = None
        self.energy_pa = None
        self.magmom = None
        self.magmom_pa = None
        self.output = None
        self.dos = None
        self.band_gap = None
        self.irreducible_kpoints = None
        self.runtime = None
        self.nsteps = None
        self.converged = None
        self.delta_e = None
        self.stability = None

    @staticmethod
    def read(path):
        """
        Reads the outcar specified by the objects path. Populates input field
        values, as well as outputs, in addition to finding errors and
        confirming convergence.

        Examples:

            >>> path = '/analysis/vasp/files/normal/standard/'
            >>> calc = Calculation.read(INSTALL_PATH+path)

        """
        path = os.path.abspath(path)
        existing = Calculation.objects.filter(path=path)
        if existing.count() > 1:
            return existing
        elif existing.count() == 1:
            return existing[0]

        calc = Calculation(path=path)
        if calc.input is None:
            calc.read_input_structure()
        calc.set_label(os.path.basename(calc.path))
        calc.read_outcar()
        calc.read_stdout()
        if calc.converged:
            calc.read_doscar()
        if not calc.output is None:
            calc.output.set_label(calc.label)
        return calc

    @staticmethod
    def read_tree(path):
        path = os.path.abspath(path)
        contents = os.listdir(path)
        prev_calcs = [ f for f in contents if 
                       os.path.isdir('%s/%s' % (path, f)) ]
        prev_calcs = sorted(prev_calcs, key=lambda x: -int(x.split('_')[0]))

        calcs = [Calculation.read(path)]
        for i, calc in enumerate(prev_calcs):
            c = Calculation.read('%s/%s' % (path, calc))
            c.set_label('%s_%s' % (calcs[0].label, calc.split('_')[0]))
            calcs[-1].input = c.output
            calcs.append(c)
        return calcs

    def address_errors(self):
        errors = self.errors
        if not errors or errors == ['found no errors']:
            logger.info('Found no errors')
            return self
        
        if self.label == '':
            self.set_label(os.path.basename(self.path))
        new_calc = self.copy()
        new_calc.set_label(self.label)
        self.set_label(self.label + '_%d' % self.attempt)
        new_calc.attempt += 1
        if new_calc.attempt > 5:
            new_calc.add_error('attempts')

        for err in errors:
            if err in ['duplicate','partial']:
                continue
            elif err == 'convergence':
                if not self.output is None:
                    new_calc.remove_error('convergence')
                    new_calc.input = self.output
                    new_calc.input.set_label(self.label)
            elif err == 'electronic_convergence':
                new_calc.fix_electronic_convergence()
            elif err == 'doscar_exc':
                new_calc.fix_bands()
            elif err == 'bands':
                new_calc.fix_bands()
            elif err == 'edddav':
                new_calc.fix_dav()
            elif err == 'errrmm':
                new_calc.fix_rmm()
            elif err == 'brions':
                new_calc.fix_brions()
            elif err == 'brmix':
                new_calc.fix_brmix()
            elif err in [ 'zpotrf', 'fexcp', 'fexcf']:
                new_calc.reduce_potim()
            elif err in ['pricel', 'invgrp', 'sgrcon']:
                new_calc.increase_symprec()
            elif err == 'hermitian':
                new_calc.fix_hermitian()
            else:
                print err
        return new_calc

    def compress(self):
        for file in os.listdir(self.path):
            if file in ['OUTCAR', 'CHGCAR', 'CHG', 'PROCAR', 'LOCPOT', 'ELFCAR']:
                os.system('gzip -f %s' % self.path+'/'+file)

    def copy(self):
        new = Calculation()
        new.entry = self.entry
        new.label = ''
        new.input = self.input
        new.output = self.output
        new.dos = self.dos
        new.path = self.path
        new.potentials = self.potentials
        new.hubbards = self.hubbards
        new.settings = self.settings
        new.attempt = self.attempt 
        new.composition = self.composition
        return new

    def move(self, path):
        path = os.path.abspath(path)
        os.system('mkdir %s 2> /dev/null' % path)
        os.system('cp %s/* %s 2> /dev/null' % (self.path, path))
        os.system('rm %s/* 2> /dev/null' % self.path)
        self.path = path
        self.save()

    def backup(self):
        new_dir = '%s_' % self.attempt
        new_dir += '_'.join(self.errors)
        new_dir = new_dir.replace(' ','')
        logger.info('backing up %s to %s' % (self.path, new_dir))
        self.move(self.path+'/'+new_dir)

    def clean_start(self):
        depth = self.path.count('/') - self.path.count('..')
        if depth < 6:
            raise ValueError('Too short path supplied to clean_start: %s' % self.path)
        else:
            os.system('rm -rf %s &> /dev/null' % self.path)

    #= Error correcting =#

    def fix_zhegev(self):
        raise NotImplementedError

    def fix_brmix(self):
        self.settings.update({'symprec':1e-7,
                              'algo':'normal'})
        self.remove_error('brmix')

    def fix_electronic_convergence(self):
        if not self.settings.get('algo') == 'normal':
            self.settings['algo'] = 'normal'
            self.remove_error('electronic_convergence')

    def increase_symprec(self):
        self.settings['symprec'] = 1e-7
        self.remove_error('invgrp')
        self.remove_error('pricel')
        self.remove_error('sgrcon')

    def fix_brions(self):
        self.settings['potim'] *= 2
        self.remove_error('brions')

    def reduce_potim(self):
        self.settings.update({'algo':'normal',
                              'potim':0.1})
        self.remove_error('zpotrf')
        self.remove_error('fexcp')
        self.remove_error('fexcf')

    def fix_bands(self):
        self.settings['nbands'] = int(np.ceil(self.settings['nbands']*1.5))
        self.errors = []

    def fix_dav(self):
        if self.settings['algo'] == 'fast':
            self.settings['algo'] = 'very_fast'
        elif self.settings['algo'] == 'normal':
            self.settings['algo'] = 'very_fast'
        else:
            return
        self.remove_error('edddav')
        self.remove_error('electronic_convergence')

    def fix_rmm(self):
        if self.settings['algo'] == 'fast':
            self.settings['algo'] = 'normal'
        elif self.settings['algo'] == 'very_fast':
            self.settings['algo'] = 'normal'
        else:
            return
        self.remove_error('errrmm')
        self.remove_error('electronic_convergence')

    def fix_hermitian(self):
        if self.settings['algo'] == 'very_fast':
            return
        self.settings['algo'] = 'very_fast'
        self.remove_error('hermitian')
        self.remove_error('electronic_convergence')

    #### calculation management

    def write(self):
        os.system('mkdir %s 2> /dev/null' % self.path)
        poscar = open(self.path+'/POSCAR','w')
        potcar = open(self.path+'/POTCAR','w')
        incar = open(self.path+'/INCAR','w')
        kpoints = open(self.path+'/KPOINTS','w')
        poscar.write(self.POSCAR)
        potcar.write(self.POTCAR)
        incar.write(self.INCAR)
        kpoints.write(self.KPOINTS)
        poscar.close()
        potcar.close()
        incar.close()
        kpoints.close()

    @property
    def estimate(self):
        return 48*8*3600

    @property
    def instructions(self):
        if self.converged:
            return {}
        elif self.errors:
            return {}

        instruction = {
                'path':self.path,
                'walltime':self.estimate,
                'header':'\n'.join(['gunzip -f CHGCAR.gz &> /dev/null',
                    'date +%s',
                    'ulimit -s unlimited']),
                'mpi':'mpirun -machinefile $PBS_NODEFILE -np $NPROCS',
                'binary':'vasp_53', 
                'pipes':' > stdout.txt 2> stderr.txt',
                'footer':'\n'.join(['gzip -f CHGCAR OUTCAR PROCAR ELFCAR',
                    'rm -f WAVECAR CHG',
                    'date +%s'])}

        if self.input.natoms < 10:
            instruction.update({'mpi':'','binary':'vasp_53_serial',
                'serial':True})
        return instruction

    def set_label(self, label):
        self.label = label
        if not self.entry is None:
            self.entry.calculations[label] = self

    def set_hubbards(self, convention='wang'):
        hubs = HUBBARDS.get(convention, {})
        elts = set( k[0] for k in hubs.keys() )
        ligs = set( k[1] for k in hubs.keys() )
        lig_int = ligs & set(self.input.comp.keys())

        if not lig_int:
            return
        elif len(lig_int) > 1:
            raise Exception('More than 1 ligand matches. No convention\
            established for this case!')
        
        if not elts & set(self.input.comp.keys()):
            return

        for atom in self.input:
            for hub in hubs:
                if ( atom.element_id == hub[0] and 
                        hub[2] in [ None, atom.ox ]):
                    self.hubbards.append(pot.Hubbard.get(
                        hub[0], lig=hub[1], ox=hub[2],
                        u=hubs[hub]['U'], l=hubs[hub]['L']))
                    break
            else:
                self.hubbards.append(pot.Hubbard.get(atom.element_id))
        self.hubbards = list(set(self.hubbards))

    def set_potentials(self, choice='vasp_rec', distinct_by_ox=False):
        if isinstance(choice, list):
            if len(self.potentials) == len(choice):
                return
        pot_set = POTENTIALS[choice]
        potentials = pot.Potential.objects.filter(xc=pot_set['xc'],
                                              gw=pot_set['gw'],
                                              us=pot_set['us'],
                                              paw=pot_set['paw'])

        pnames = [ pot_set['elements'][e.symbol] for e in self.elements ]
        self.potentials = list(potentials.filter(name__in=pnames))

    def set_magmoms(self, ordering='ferro'):
        self.input.set_magnetism(ordering)
        if any(self.input.magmoms):
            self.ispin = 2

    def set_wavecar(self, source):
        """
        Copy the WAVECAR specified by `source` to this calculation.

        Arguments:
            source: can be another :mod:`~qmpy.Calculation` instance or a
            string containing a path to a WAVECAR. If it is a path, it should 
            be a absolute, i.e. begin with "/", and can either end with the 
            WAVECAR or simply point to the path that contains it. For
            example, if you want to take the WAVECAR from a previous 
            calculation you can do any of::
            
            >>> c1 # old calculation
            >>> c2 # new calculation
            >>> c2.set_wavecar(c1)
            >>> c2.set_wavecar(c1.path)
            >>> c2.set_wavecar(c1.path+'/WAVECAR')

        """
        if isinstance(source, Calculation):
            source = calculation.path

        source = os.path.abspath(source)
        if not os.path.exists(source):
            raise VaspError('WAVECAR does not exist at %s', source) 

        if not 'WAVECAR' in source:
            files = os.listdir(source)
            for f in files:
                if 'WAVECAR' in f:
                    new_path = '%s/%s' % (source, f)
                    self.set_wavecar(new_path)
        else:
            subprocess.check_call(['cp', source, self.path])

    def set_chgcar(self, source):
        """
        Copy the CHGCAR specified by `source` to this calculation.

        Arguments:
            source: can be another :mod:`~qmpy.Calculation` instance or a
            string containing a path to a CHGCAR. If it is a path, it should 
            be a absolute, i.e. begin with "/", and can either end with the 
            CHGCAR or simply point to the path that contains it. For
            example, if you want to take the CHGCAR from a previous 
            calculation you can do any of::
            
            >>> c1 # old calculation
            >>> c2 # new calculation
            >>> c2.set_chgcar(c1)
            >>> c2.set_chgcar(c1.path)
            >>> c2.set_chgcar(c1.path+'/CHGCAR')

        """
        if isinstance(source, Calculation):
            source = source.path

        source = os.path.abspath(source)
        if not os.path.exists(source):
            raise VaspError('CHGCAR does not exist at %s', source) 

        if not 'CHGCAR' in source:
            files = os.listdir(source)
            for f in files:
                if 'CHGCAR' in f:
                    new_path = '%s/%s' % (source, f)
                    self.set_chgcar(new_path)
        else:
            logger.debug('Copying: %s to %s', source, self.path)
            subprocess.check_call(['cp', source, self.path])

    @property
    def volume(self):
        if self.output:
            return self.output.get_volume()
        elif self.input:
            return self.input.get_volume()

    @property
    def volume_pa(self):
        if self.volume is None:
            return
        return self.volume/len(self.output)

    def compute_formation(self, reference='standard'):
        if not self.converged:
            return None
        if len(self.input.comp) == 1:
            e = comp.Composition.get(self.input.comp).total_energy
            formation = fe.FormationEnergy.get(self, fit=reference)
            formation.delta_e = self.energy_pa - e
            formation.composition = self.input.composition
            formation.entry = self.entry
            self.formation = formation
            return formation
        hub_mus = chem_pots[reference]['hubbards']
        if self.hub_comp and reference == 'nothing':
            return
        elt_mus = chem_pots[reference]['elements']
        adjust = 0
        adjust -= sum([ hub_mus.get(k.key, 0)*v for k,v in self.hub_comp.items() ])
        adjust -= sum([ elt_mus[k]*v for k,v in self.comp.items() ])
        formation = fe.FormationEnergy.get(self, fit=reference)
        formation.delta_e = ( self.energy + adjust ) / self.natoms
        formation.composition = self.input.composition
        formation.entry = self.entry
        self.formation = formation
        return formation

    @staticmethod
    def setup(input=None, configuration='standard', path=None, entry=None,
            hubbard='wang', potentials='vasp_rec', settings={}, 
            chgcar=None, wavecar=None,
            **kwargs):
        
        if path is None:
            path = os.path.abspath(entry.path)
        else:
            path = os.path.abspath(path)

        if Calculation.objects.filter(path=path).exists():
            calc = Calculation.objects.get(path=path)
        else:
            if not os.path.exists(path):
                os.mkdir(path)
            calc = Calculation()
            calc.path = path
            calc.configuration = configuration
            if chgcar:
                calc.set_chgcar(chgcar)
            if wavecar:
                calc.set_wavecar(wavecar)
            calc.input = input
            calc.kwargs = kwargs
            if entry:
                calc.entry = entry

        if configuration not in VASP_SETTINGS:
            raise NotImplementedError('That configuration does not exist!')

        calc.input.make_primitive()

        settings = {}
        if calc.input.natoms > 20:
            settings['lreal'] = 'auto'
        settings.update(VASP_SETTINGS[configuration])
        settings.update(settings)
        calc.set_potentials(calc.settings.get('potentials', 'vasp_rec'))
        calc.set_hubbards(calc.settings.get('hubbards', 'wang'))
        calc.set_magmoms(calc.settings.get('magnetism', 'ferro'))

        if 'scale_encut' in settings:
            enmax = max(pot.enmax for pot in calc.potentials)
            calc.encut = int(settings.get('scale_encut')*enmax)

        calc.settings = settings
        if calc.input.natoms >= 10:
            calc.settings.update({
                'ncore': 4, 
                'lscalu': False,
                'lplane': True})

        #= Error handling stuff =#
        try:
            calc.get_outcar()
        except VaspError:
            if not ( os.path.exists(calc.path+'/INCAR') and
                    os.path.exists(calc.path+'/POTCAR') and 
                    os.path.exists(calc.path+'/KPOINTS') and
                    os.path.exists(calc.path+'/POSCAR')):
                calc.write()
            return calc

        calc.read_outcar()
        calc.read_doscar()
        calc.read_stdout()

        if calc.converged:
            return calc
        elif not calc.errors:
            calc.write()
            return calc
        
        fixed_calc = calc.address_errors()
        if fixed_calc.errors:
            # unable to fix errors
            raise VaspError("Unable to fix errors: %s", fixed_calc.errors)

        fixed_calc.set_magmoms(calc.settings.get('magnetism', 'ferro'))
        fixed_calc.clear_results()
        calc.backup()
        fixed_calc.clear_outputs()
        fixed_calc.set_chgcar(calc)
        fixed_calc.write()
        return fixed_calc
