# qmpy/materials/structure.py
"""
The Structure class is used to represent a crystal structure.

"""

import numpy as np
import numpy.linalg as la
import time
import copy
import random
from collections import defaultdict
import logging

from django.db import models
from django.db import transaction

import qmpy
from qmpy.utils import *
from element import Element, Species
from atom import Atom, Site
from composition import Composition
from qmpy.utils import *
from qmpy.data.meta_data import *
from qmpy.analysis.symmetry import *
from qmpy.analysis import *

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

class StructureError(Exception):
    """Structure related problem"""

@add_meta_data('comment')
@add_meta_data('keyword')
class Structure(models.Model, object):
    """
    Structure model. Principal attributes are a lattice and basis set.

    Relationships:
        | atom_set
        | calculated
        | composition
        | element_set
        | entry
        | fit
        | spacegroup
        | species_set
        | prototype
        | reference
        | site

    Attributes:
        | **Identification**
        | id
        | label
        | meta_data
        | natoms
        | nsites
        | ntypes
        | measured
        | source
        | 
        | **Lattice**
        | x1, x2, x3
        | y1, y2, y3
        | z1, z2, z3: Lattice vectors of the cell
        | volume
        | volume_pa
        |
        | **Calculated properties**
        | delta_e
        | energy
        | energy_pa
        | magmom
        | magmom_pa
        | sxx, sxy, syy
        | syx, szx, szz: Stresses on the cell
        | meta_stability


    """
    entry = models.ForeignKey('Entry', null=True)
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    meta_data = models.ManyToManyField('MetaData')
    reference = models.ForeignKey('Reference', null=True)
    label = models.CharField(blank=True, max_length=63)
    prototype = models.ForeignKey('Prototype', null=True, blank=True,
                                               related_name='+')
    measured = models.BooleanField(default=False)

    composition = models.ForeignKey('Composition', null=True, 
                                    related_name='structure_set')
    natoms = models.IntegerField(null=True, blank=True)
    nsites = models.IntegerField(null=True, blank=True)
    ntypes = models.IntegerField(null=True, blank=True)

    x1 = models.FloatField()
    x2 = models.FloatField()
    x3 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    y3 = models.FloatField()
    z1 = models.FloatField()
    z2 = models.FloatField()
    z3 = models.FloatField()

    volume = models.FloatField(blank=True, null=True)
    volume_pa = models.FloatField(blank=True, null=True)

    sxx = models.FloatField(default=0)
    syy = models.FloatField(default=0)
    szz = models.FloatField(default=0)
    sxy = models.FloatField(default=0)
    syz = models.FloatField(default=0)
    szx = models.FloatField(default=0)

    spacegroup = models.ForeignKey('Spacegroup', blank=True,
            null=True)

    energy = models.FloatField(blank=True, null=True)
    energy_pa = models.FloatField(blank=True, null=True)
    magmom = models.FloatField(blank=True, null=True)
    magmom_pa = models.FloatField(blank=True, null=True)
    delta_e = models.FloatField(blank=True, null=True)
    meta_stability = models.FloatField(blank=True, null=True)
    fit = models.ForeignKey('Fit', blank=True, null=True)

    _reciprocal_lattice = None
    _distinct_atoms = []
    _magmoms = []

    class Meta:
        app_label = 'qmpy'
        db_table = 'structures'

    def __eq__(self, other):
        return self.compare(other)

    def __str__(self):
        return format_comp(reduce_comp(self.comp))

    def __getitem__(self, i):
        return self.atoms[i]

    def __len__(self):
        return len(self.atoms)

    @staticmethod
    def create(cell, atoms=[], **kwargs):
        """
        Creates a new Structure.

        Arguments:
            cell: 3x3 lattice vector array

        Keyword Arguments:
            atoms: List of ``Atom`` creation arguments. Can be a list of 
            [element, coord], or a list of [element, coord, kwargs].

        Examples:
            >>> a = 3.54
            >>> cell = [[a,0,0],[0,a,0],[0,0,a]]
            >>> atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
            >>> s = Structure.create(cell, atoms)
            >>> atoms = [('Cu', [0,0,0], {'magmom':3}),
                    ('Cu', [0.5, 0.5, 0.5], {'magmom':-3})]
            >>> s2 = Structure.create(cell, atoms)

        """
        s = Structure(**kwargs)
        if np.shape(cell) == (6,):
            s.lat_params = cell
        elif np.shape(cell) == (3,3):
            s.cell = cell
        elif np.shape(cell) == (3,):
            s.cell = np.eye(3)*cell

        for atom in atoms:
            if len(atom) == 2:
                atom = Atom.create(*atom)
            elif len(atom) == 3:
                atom = Atom.create(atom[0], atom[1], **atom[2])
            s.add_atom(atom)
        return s

    @transaction.atomic
    def save(self,*args, **kwargs):
        if not self.composition:
            self.composition = Composition.get(self.comp)

        if not self.spacegroup:
            self.symmetrize()

        self.natoms = len(self.atoms)
        self.nsites = len(self.sites)
        self.ntypes = len(self.comp.keys())
        self.get_volume()
        super(Structure, self).save(*args, **kwargs)
        if self._atoms:
            for a in self.atoms:
                a.structure = self
                a.save()
            #self.atom_set = self.atoms
        if self._sites:
            for s in self.sites:
                s.structure = self
                s.save()
            #self.site_set = self.sites
        self.element_set = self.elements
        self.species_set = self.species
        self.meta_data = self.comment_objects + self.keyword_objects

    _atoms = None
    @property
    def atoms(self):
        """
        List of ``Atoms`` in the structure. 
        """
        if self._atoms is None:
            if not self.id:
                self._atoms = []
            else:
                self._atoms = self.atom_set.all()
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        self._atoms = atoms
        self.natoms = len(atoms)
        self.ntypes = len(self.comp)
        for a in atoms:
            a.structure = self

    _sites = None
    @property
    def sites(self):
        """
        List of ``Sites`` in the structure.
        """
        if self._sites is None:
            self._sites = self.get_sites()
        return self._sites

    @sites.setter
    def sites(self, sites):
        self._sites = sites
        for s in sites:
            s.structure = self
        self.nsites = len(sites)

    @property
    def elements(self):
        """List of Elements"""
        return [ Element.get(e) for e in self.comp.keys() ]

    @property
    def species(self):
        """List of species"""
        return [ Species.get(s) for s in self.spec_comp.keys() ]

    @property
    def stresses(self):
        """Calculated stresses, a numpy.ndarray of shape (6,)"""
        return np.array([self.sxx, self.syy, self.szz,
            self.sxy, self.syz, self.szx ])
        
    @stresses.setter
    def stresses(self, vector):
        self.sxx, self.syy, self.szz = vector[0:3]
        self.sxy, self.syz, self.szx = vector[3:6]

    def get_volume(self):
        """Calculates the volume from the triple product of self.cell"""
        b1, b2, b3 = self.cell
        self.volume = abs(np.dot(np.cross(b1, b2), b3))
        self.volume_pa = self.volume/len(self)
        return self.volume

    def set_volume(self, value):
        """
        Rescales the unit cell to the specified volume, keeping the direction
        and relative magnitudes of all lattice vectors the same.
        """
        scale = value/self.volume
        self.cell = self.cell * scale**(1/3.)
        self.volume_pa = value/self.natoms
        self.volume = value

    @property
    def lat_param_dict(self):
        """Dictionary of lattice parameters."""
        return dict(zip( ['a', 'b', 'c', 'alpha', 'beta', 'gamma'], 
                         self.lat_params))

    _lat_params = None
    @property
    def lat_params(self):
        """Tuple of lattice parameters (a, b, c, alpha, beta, gamma)."""
        if self._lat_params is None:
            self._lat_params = basis_to_latparams(self.cell)
        return self._lat_params

    @lat_params.setter
    def lat_params(self, lat_params):
        self.cell = latparams_to_basis(lat_params)
        self._lat_params = lat_params

    lp = lat_params

    @property
    def cell(self):
        """Lattice vectors, 3x3 numpy.ndarray."""
        return np.array([
                [self.x1, self.x2, self.x3],
                [self.y1, self.y2, self.y3],
                [self.z1, self.z2, self.z3]])

    @cell.setter
    def cell(self, cell):
        self.x1, self.x2, self.x3 = cell[0]
        self.y1, self.y2, self.y3 = cell[1]
        self.z1, self.z2, self.z3 = cell[2]
        self._lat_params = None
        self._inv = None

    @property
    def metrical_matrix(self):
        """np.dot(self.cell.T, self.cell)"""
        A = np.dot(self.cell[0], self.cell[0])
        B = np.dot(self.cell[1], self.cell[1])
        C = np.dot(self.cell[2], self.cell[2])
        X = np.dot(self.cell[1], self.cell[2])
        Y = np.dot(self.cell[0], self.cell[2])
        Z = np.dot(self.cell[0], self.cell[1])
        return np.array([[A, Z, Y],
                         [Z, B, X],
                         [Y, X, C]])

    @metrical_matrix.setter
    def metrical_matrix(self, G):
        a = np.sqrt(abs(G[0,0]))
        b = np.sqrt(abs(G[1,1]))
        c = np.sqrt(abs(G[2,2]))
        al = np.arccos(G[1,2]/abs(b*c))*180/np.pi
        be = np.arccos(G[0,2]/abs(a*c))*180/np.pi
        ga = np.arccos(G[0,1]/abs(a*b))*180/np.pi
        self.cell = latparams_to_basis([a, b, c, al, be, ga])

    @property
    def atomic_numbers(self):
        """List of atomic numbers, length equal to number of atoms."""
        return np.array([ atom.element.z for atom in self.atoms ])

    @property
    def atom_types(self):
        """List of atomic symbols, length equal to number of atoms."""
        return np.array([ atom.element_id for atom in self.atoms ])

    @atom_types.setter
    def atom_types(self, elements):
        for a, e in zip(self.atoms, elements):
            a.element_id = e

    @property
    def species_types(self):
        """List of species, length equal to number of atoms."""
        return np.array([ atom.species_id for atom in self.atoms ])

    def symmetrize(self, tol=1e-5, angle_tol=-1):
        """
        Analyze the symmetry of the structure. Uses spglib to find the
        symmetry. 

        symmetrize sets:
         * spacegroup -> Spacegroup
         * uniq_sites -> list of unique Sites
         * orbits -> lists of equivalent Atoms
         * rotations -> List of rotation operations
         * translations -> List of translation operations
         * operatiosn -> List of (rotation,translation) pairs
         * for each atom: atom.wyckoff -> WyckoffSite
         * for each site: site.multiplicity -> int

        """
        dataset = get_symmetry_dataset(self, 
                                       symprec=tol)
        self.spacegroup = Spacegroup.objects.get(pk=dataset['number'])
        for i, site in enumerate(self.sites):    
            site.wyckoff = self.spacegroup.get_site(dataset['wyckoffs'][i])
            site.structure = self
        counts = defaultdict(int)
        orbits = defaultdict(list)
        for e in dataset['equivalent_atoms']:
            counts[e] += 1
            orbits[e].append(self.atoms[e])
        self.operations = zip(dataset['rotations'], dataset['translations'])
        rots = []
        for r in dataset['rotations']:
            if not any([ np.allclose(r, x) for x in rots ]):
                rots.append(r)
        self.rotations = rots
        trans = []
        for t in dataset['translations']:
            if not any([ np.allclose(t, x) for x in trans ]):
                trans.append(t)
        self.translations = trans
        self.orbits = orbits.values()
        self.uniq_sites = []
        for ind, mult in counts.items():
            site = self.sites[ind]
            site.multiplicity = mult
            self.uniq_sites.append(site)

    def pdf_compare(self, other, tol=1e-2):
        """
        Compute the PDF for each structure and evaluate the overlap integral
        for all pairs of species.
        """

        elts = list(set([a.element_id for a in self ])) 
        dists = get_pair_distances(self)
        odists = get_pair_distances(other)
        for e1, e2 in itertools.combinations(elts,2):
            d1 = dists[frozenset([e1,e2])]
            d2 = odists[frozenset([e1,e2])]
            for x, y in zip(d1, d2):
                if abs(x-y) > tol:
                    return False
        return True

    def compare(self, other, tol=1e-2):
        """
        Credit to K. Michel for the algorithm.

        1. Check that elements are the same in both structures

        2. Convert both structures to primitive form

        3. Check that the total number of atoms in primitive cells are the same

        4. Check that the number of atoms of each element are the same in
        primitive cells

        5. If needed check that the primitive cell volumes are the same

        6. Convert both primitive cells to reduced form There is one issue here - 
        the reduce cell could be type I (all angles acute) or type II (all angles 
        obtuse) and a slight difference in the initial cells could cause two 
        structures to reduce to different types. So at this step, if the angles 
        are not correct, the second cell is transformed as 
        [[-1, 0, 0], [0, -1, 0], [0, 0, 1]].

        7. Check that the cell internal angles are the same in both reduced
        cells. 

        8. Check that the ratios of reduced cell basis lengths are the same. ie
        a1/b1 = a2/b2, a1/c1 = a2/c2, and b1/c1 = b2/c2 where a1, b1, c1, are
        the lengths of basis vectors in cell 1 and a2, b2, c2 are the lengths
        of cell 2.

        9. Get the lattice symmetry of the reduced cell 2 (this is a list of
        all rotations that leave the lattice itself unchanged). In turn, apply
        all rotations to reduced cell 2 and for each search for a vector that
        overlaps rotated cell positions with positions in reduced cell 1. If a
        rotation + translation overlaps reduced cells, then they are the same.

        Arguments:
            other: Another ``Structure``.

        Keyword Arguments:
            tol: Percent deviation in lattice parameters and angles.

        """

        # 1
        if not self.elements == other.elements:
            logger.debug("Structure comparison: element mismatch")
            return False

        # 2
        self.make_primitive()
        other.make_primitive()

        # 3
        if not self.natoms == other.natoms:
            logger.debug("Structure comparison: natom mismatch")
            return False

        # 4
        if not self.comp == other.comp:
            logger.debug("Structure comparison: composition mismatch")
            return False

        # 5 (optional)
        #v1, v2 = self.get_volume(), other.get_volume()
        #if abs(v1 - v2)/min(v1, v2) > tol:
        #    logger.debug("Structure comparison: volume mismatch")
        #    return False

        # 6
        self.reduce()
        other.reduce()

        if any([ a > 90 for a in self.lat_params[3:]]):
            logger.debug("Structure comparison: converting self from type II to type I.")
            self.transform([-1,-1,1])

        if any([ a > 90 for a in other.lat_params[3:]]):
            logger.debug("Structure comparison: converting other from type II to type I.")
            other.transform([-1,-1,1])

        # 7
        for a, b in zip(self.lat_params[3:], other.lat_params[3:]):
            if abs((a-b)/min(a,b)) > tol:
                logger.debug("Structure comparison: lat param mismatch")
                return False

        # 8
        ratios = [ x/y for x,y in zip(self.lp[:3], other.lp[:3])]
        for a,b in itertools.combinations(ratios, r=2):
            if abs(a-b)/min(a,b) > tol:
                logger.debug("Structure comparison: lattice vector ratio mismatch")
                return False

        # 9
        min_elt = sorted(self.comp, key=lambda x: self.comp[x])[0]
        self.symmetrize()
        #self.sort()
        for rot in self.rotations:
            # try mapping each atom onto other atoms of the same type
            inv = la.inv(rot)
            for i, a1 in enumerate(self.atoms):
                if a1.element_id != min_elt:
                    continue
                coords = np.array([ inv.dot(c) for c in other.coords ])
                coords %= 1.0
                coords %= 1.0
                for j, a2 in enumerate(other.atoms):
                    if a1.species != a2.species:
                        continue
                    t = coords[j] - a1.coord
                    tcoords = coords - t
                    tcoords %= 1.0
                    tcoords %= 1.0
                    # check 
                    match = True
                    for k, atom in enumerate(other.atoms):
                        atom = Atom.create(atom.element_id, tcoords[k])
                        if not self.contains(atom, tol=50*tol):
                            match = False
                            break

                    if match:
                        return True
        logger.debug("Atoms don't match.")
        return False

    def contains(self, b, tol=0.1):
        for a in self.atoms:
            if not a.element_id == b.element_id:
                continue
            #ca = [ x - 1 if x >= 0.5 else x for x in a.coord ]
            #cb = [ x - 1 if x >= 0.5 else x for x in b.coord ]
            #lp = self.lat_params
            #if any([ abs(ca[i]-cb[i])*lp[i] > tol for i in range(3)]):
            #    continue
            if self.get_distance(a, b) < tol:
                return True
        return False

    def get_distance(self, atom1, atom2):
        """Return the shorted distance between two atoms in the structure."""
        if isinstance(atom1, int):
            atom1 = self.atoms[atom1].coord
        elif isinstance(atom1, (Atom,Site)):
            atom1 = atom1.coord
        if isinstance(atom2, int):
            atom2 = self.atoms[atom2].coord
        elif isinstance(atom2, (Atom,Site)):
            atom2 = atom2.coord

        vec = atom1 - atom2
        dist = np.dot(vec - np.round(vec), self.cell)
        return la.norm(dist)

    def add_atom(self, b, tol=0.1):
        if self.contains(b, tol=tol):
            return
        self._atoms.append(b)
        self.spacegroup = None

    def sort(self):
        self.atoms = sorted(self.atoms)

    def set_composition(self, value=None):
        if value is None:
            self.composition = Composition.get(self.comp)
        return self.composition

    def set_magnetism(self, type, scheme='primitive'):
        """
        Assigns magnetic moments to all atoms in accordance with the specified
        magnetism scheme.

        Schemes:

        +---------+-------------------------------------+
        | Keyword | Description                         |
        +=========+=====================================+
        |  None   | all magnetic moments = None         |
        +---------+-------------------------------------+
        | "ferro" | atoms with partially filled d and   |
        |         | f shells are assigned a magnetic    |
        |         | moment of 5 mu_b                    |
        +---------+-------------------------------------+
        | "anti"  | finds a highly ordererd arrangement |
        |         | arrangement of up and down spins.   |
        |         | If only 1 magnetic atom is found    |
        |         | a ferromagnetic arrangment is used. |
        |         | raises NotImplementedError          |
        +---------+-------------------------------------+

        """
        if type == 'none':
            for atom in self.atoms:
                atom.magmom = 0
                if atom.id is not None:
                    atom.save()
        if type == 'ferro':
            for atom in self.atoms:
                if atom.element.d_elec > 0 and atom.element.d_elec < 10:
                    atom.magmom = 5
                elif atom.element.f_elec > 0 and atom.element.f_elec < 14:
                    atom.magmom = 7
                else:
                    atom.magmom = 0
                if atom.id is not None:
                    atom.save()
        elif type == 'anti-ferro':
            raise NotImplementedError
        self.spacegroup = None

    @property
    def comp(self):
        """Composition dictionary."""
        comp = {}
        for atom in self.atoms:
            elt = atom.element_id
            comp[elt] = comp.get(elt, 0) + atom.occupancy
        return comp

    @property
    def spec_comp(self):
        """Species composition dictionary."""
        spec_comp = {}
        for atom in self.atoms:
            spec = atom.species
            spec_comp[spec] = spec_comp.get(spec, 0) + atom.occupancy
        return spec_comp

    @property
    def name(self):
        """Unformatted name."""
        return format_comp(self.comp)

    @property
    def html(self):
        return html_comp(self.comp)

    @property
    def unit_comp(self):
        """Composition dict, where sum(self.unit_comp.values()) == 1"""
        return unit_comp(self.comp)

    @property
    def coords(self):
        """numpy.ndarray of atom coordinates of shape (3, natoms)."""
        return np.array([ map(float, atom.coord) for atom in self.atoms ])

    @coords.setter
    def coords(self, coords):
        if len(coords) != len(self.atoms):
            raise ValueError
        for a, c in zip(self.atoms, coords):
            c = np.array(map(float,c))
            c %= 1.0
            c %= 1.0
            a.coord = c

    @property
    def magmoms(self):
        """numpy.ndarray of magnetic moments of shape (natoms,)."""
        return np.array([ atom.magmom for atom in self.atoms ])

    @magmoms.setter
    def magmoms(self, moms):
        for mom, atom in zip(self, moms):
            atom.magmom = mom

    @property
    def site_coords(self):
        """numpy.ndarray of site coordinates of shape (3, nsites)."""
        return np.vstack([ s.coord for s in self.sites ])

    @property
    def site_labels(self):
        """
        Labels for all sites. For sites with single occupancy returns the
        atomic symbol, for sites with multiple occupancies returns "(A,B)".

        """
        return np.array([ str(s) for s in self.sites ])

    @property
    def cartesian_coords(self):
        """Return atomic positions in cartesian coordinates."""
        coords = []
        for atom in self.atoms:
            if atom.direct:
                coords.append(np.dot(atom.coord, self.cell))
            else:
                coords.append(atom.coord)
        return np.array(coords)

    @property
    def forces(self):
        """numpy.ndarray of forces on atoms."""
        forces = []
        for atom in self.atoms:
            forces.append(atom.forces)
        return np.array(forces)

    @forces.setter
    def forces(self, forces):
        for forces, atom in zip(forces, self.atoms):
            atom.forces = force

    @property
    def reciprocal_lattice(self):
        """Reciprocal lattice of the structure."""
        if self._reciprocal_lattice is None:
            self._reciprocal_lattice = la.inv(self.cell).T
        return self._reciprocal_lattice

    _inv = None
    @property
    def inv(self):
        """
        Precalculates the inverse of the lattice, for faster conversion
        between cartesian and direct coordinates.
        
        """
        if self._inv is None:
            self._inv = la.inv(self.cell)
        return self._inv

    @property
    def relative_rec_lat(self):
        rec_lat = self.reciprocal_lattice
        rec_mags = map(la.norm, rec_lat)
        r0 = min(rec_mags)
        return np.array([ np.round(r/r0, 4) for r in rec_mags ])

    def get_kpoint_mesh(self, kppra):
        recs = self.reciprocal_lattice
        rec_mags = [ norm(recs[0]), norm(recs[1]), norm(recs[2])]
        r0 = max(rec_mags)
        refr = np.array([ np.round(r/r0, 4) for r in rec_mags ])
        scale = 1.0
        kpts = np.ones(3)

        while self.natoms*np.product(kpts) < kppra:
            prev_kpts = kpts.copy()
            refk = np.array(np.ones(3)*refr)*scale
            kpts = np.array(map(np.ceil, refk))
            scale += 1

        upper = kppra - np.product(prev_kpts)*self.natoms
        lower = np.product(kpts)*self.natoms - kppra
        if upper < lower:
            kpts = prev_kpts.copy()
        return kpts

    _mrd = None
    @property
    def minimum_repeat_distance(self):
        if self._mrd is None:
            self._mrd = min(self.lat_params[:3])
        return self._mrd

    def copy(self):
        """
        Create a complete copy of the structure, with any primary keys
        removed, so it is not associated with the original.

        """
        new = copy.deepcopy(self)
        new.id = None
        new.label = ''
        atom_set = []
        for atom in self.atoms:
            new_atom = atom.copy()
            new_atom.id = None
            atom_set.append(new_atom)
        new.atoms = atom_set
        return new

    @property
    def similar(self):
        return Structure.objects.filter(natoms=self.natoms,
                composition=self.composition, 
                spacegroup=self.spacegroup,
                label=self.label).exclude(id=self.id)

    def set_natoms(self, n):
        """Set self.atoms to n blank Atoms."""
        self.atoms = [ Atom() for i in range(n) ]

    def make_conventional(self):
        """Uses spglib to convert to the conventional cell.
        
        .. warning:: 
            Does not handle partial occupancy. If the cell is partially
            occupied, it is returned as is.

        Example:
            >>> s = io.read(INSTALL_PATH+'io/files/POSCAR_FCC_prim')
            >>> print len(s)
            1
            >>> s.make_conventional()
            >>> print len(s)
            4
        """
        refine_cell(self)
        v0 = self.get_volume()
        self.reduce()
        v1 = self.get_volume()
        if abs(v1 - v0) > 1e-5:
            raise StructureError('Volume changed: %s to %s' % (v0, v1))

    def make_primitive(self):
        """Uses spglib to convert to the primitive cell.
        
        .. warning:: 
            Does not handle partial occupancy. If the cell is partially
            occupied, it is returned as is.

        Example:
            >>> s = io.read(INSTALL_PATH+'io/files/POSCAR_FCC')
            >>> print len(s)
            4
            >>> s.make_primitive()
            >>> print len(s)
            1
        """
        if any( a.occupancy < 1 for a in self ):
            return
        find_primitive(self)

    def get_sites(self, tol=0.1):
        """
        From self.atoms, creates a list of Sites. Atoms which are closer
        than tol from one another are considered on the same site.

        """
        if not any([ a.occupancy < 1 for a in self.atoms ]):
            self._sites = [ a.as_site() for a in self.atoms ]
            return self._sites
        d_sites = []
        for atom in self:
            for site in d_sites:
                if atom.is_on(site):
                    site.atoms.append(atom)
                    break
            else:
                site = atom.as_site()
                site.structure = self
                d_sites.append(site)
        self._sites = d_sites
        return self._sites

    def group_atoms_by_symmetry(self):
        """Sort self.atoms according to the site they occupy."""
        eq = get_symmetry_dataset(self)['equivalent_atoms']
        resort = np.argsort(eq)
        self._atoms = list(np.array(self._atoms)[resort])

    def is_buerger_cell(self, tol=1e-5):
        G = self.metrical_matrix
        if G[0,0] < G[1,1] - tol or G[1,1] < G[2,2] - tol:
            return False
        if abs(G[0,0] - G[1,1]) < tol:
            if abs(G[1,2]) > abs(G[0,2]) - tol:
                return False
        if abs(G[1,1] - G[2,2]) < tol:
            if abs(G[0,2]) > abs(G[0,1]) - tol:
                return False

    def is_niggli_cell(self, tol=1e-5):
        if not self.is_grueber_cell():
            return False
        (a,b,c),(d,e,f) = self.niggli_form
        if abs(d-b) < tol:
            if f > 2*e - tol:
                return False
        if abs(e-a) < tol:
            if f > 2*d - tol:
                return False
        if abs(f-a) < tol:
            if e > 2*d - tol:
                return False
        if abs(d+b) < tol:
            if abs(f) > tol:
                return False
        if abs(e+a) < tol:
            if abs(f) > tol:
                return False
        if abs(f+a) < tol:
            if abs(f) > tol:
                return False
        if abs(d+e+f+a+b) < tol:
            if 2*a+2*e+f > -tol:
                return False
        return True

    def find_nearest_neighbors(self, tol=0.1):
        self._neighbor_dict = find_closest(self, tol=tol)

    _neighbor_dict = None
    @property
    def nearest_neighbor_dict(self):
        if self._neighbor_dict is None:
            self.find_nearest_neighbors()
        return self._neighbor_dict

    def get_sublattice(self, element, new=True):
        if new:
            struct = self.copy()
            return struct.get_sublattice(element, new=False)
        self.atoms = [ a for a in self if a.element_id == element ]
        return self

    def get_spin_lattice(self, element=None, supercell=None):
        if supercell:
            self.transform(supercell)
        pairs = []
        if element:
            struct = self.get_sublattice(element)
            return struct.get_lattice_network()
        self.find_nearest_neighbors()
        for a1 in self.atoms:
            for a2 in a1.neighbors:
                pairs.append([a1, a2])

        lattice = SpinLattice(pairs)
        return lattice

    def displace_atom(structure, index, vector):
        vector = np.array(vector)
        if not vector.shape == (3,):
            raise ValueError('Provide a 3x1 translation array')

        structure[index].coord += vector
        return structure

    def joggle_atoms(self, distance=1e-3, in_place=True):
        """
        Randomly displace all atoms in each direction by a distance up to +/- the
        distance keyword argument.

        Optional keyword arguments:
            *distance*      : Range within all internal coordinates are
                                displaced. Default=1e-3
            *in_place*      : If True, returns an ndarray of the applied
                                translations. If False, returns (Structure,
                                translations).

        Examples:
            >>> s = io.read('POSCAR')
            >>> s2, trans = s.joggle_atoms(in_place=False)
            >>> trans = s.joggle_atoms(1e-1)
            >>> trans = s.joggle_atoms(distance=1e-1)

        """

        if not in_place:
            new = self.copy()
            new.joggle_atoms(distance=distance)
            return new

        def disp():
            dists = np.array(self.lp[:3])*distance
            rands = [ random.random() for i in range(3) ]
            return dists*rands

        translations = np.zeros(np.shape(self.coords))
        for i, atom in enumerate(self.atoms):
            tvec = disp()
            translations[i,:] = tvec
            atom.coord += tvec
        return translations

    def recenter(self, atom, in_place=True):
        """
        Translate the internal coordinates to center the specified atom. Atom
        can be an actual Atom from the Structure.atoms list, or can be
        identified by index.

        Optional keyword arguments:
            *in_place*  : If False, return a new Structure with the
                            transformation applied.

        Examples:
            >>> s = io.read('POSCAR')
            >>> s.recenter(s[2])
            >>> s2 = s.recenter(s[0], in_place=False)
            >>> s2.recenter(2)
            >>> s == s2
            True

        """
        if not in_place:
            new = self.copy()
            new.recenter(atom, in_place=True)
            return new
        
        if isinstance(atom, int):
            atom = structure[atom]
        return self.translate(-atom.coord+0.5, cartesian=False, in_place=True)

    def translate(self, cv, cartesian=True, in_place=True):
        """
        Shifts the contents of the structure by a vector. 

        Optional keyword arguments:
            *cartesian*     : If True, translation vector is taken to be
                                cartesian coordinates. If False, translation
                                vector is taken to be in fractional
                                coordinates. Default=True
            *in_place*      : If False, return a new Structure with the
                                transformation applied.

        Examples:
            >>> s = io.read('POSCAR')
            >>> s.translate([1,2,3])
            >>> s.translate([0.5,0.5, 0.5], cartesian=False)
            >>> s2 = s.translate([-1,2,1], in_place=False)

        """

        if not in_place:
            new = self.copy()
            new.translate(cv, cartesian=cartesian, in_place=True)
            return new

        cv = np.array(cv)
        if not cv.shape == (3,):
            raise ValueError

        if all([ abs(v) < 1e-4 for v in cv]):
            return self

        if cartesian:
            cv = np.array(map(float, np.dot(self.inv.T, cv)))

        coords = self.coords + cv
        coords = coords % 1.0
        self.coords = coords % 1.0
        return self

    def transform(self, transform, in_place=True):
        """
        Apply lattice transform to the structure. Accepts transformations of
        shape (3,) and (3,3).
        
        Optional keyword arguments:
            *in_place*      : If False, return a new Structure with the
                                transformation applied.

        Examples:
            >>> s = io.read('POSCAR')
            >>> s.transform([2,2,2]) # 2x2x2 supercell
            >>> s.transform([[0,1,0],[1,0,0],[0,0,1]]) # swap axis 1 for 2
            >>> s2 = s.transform([2,2,2], in_place=False)

        """
        if not in_place:
            new = self.copy()
            new.transform(transform)
            return new

        transform = np.array(transform)
        if transform.shape == (3,3):
            pass
        elif transform.shape in [ (1,3), (3,) ]:
            transform = np.eye(3)*transform
        else:
            raise ValueError

        if la.det(transform) == 1:
            # if cell size doesn't change
            new_cell = transform.dot(self.cell)
            inv = la.inv(transform.T)
            coords = np.array([ inv.dot(c) for c in self.coords ])
            coords %= 1.0
            coords %= 1.0
            self.coords = coords
            self.cell = new_cell
            return self

        # construct the new lattice
        cell = list(self.cell)
        new_cell = transform.dot(cell)

        # fill with atoms
        basis = list(self.cartesian_coords)
        elts = list(self.atom_types)
        limits = [ int(max(abs(transform[:,i]))) for i in range(3) ] 
        ranges = [ range(-l, l+1) for l in limits ]
        n_cells = len(ranges[0])*len(ranges[1])*len(ranges[2])

        sc = np.vstack([ basis + np.dot(ijk, cell) for ijk in
                            itertools.product(*ranges)])
        tmp_elts = elts*n_cells

        # remove atoms not in lattice
        cell_inv = la.inv(new_cell.T)
        new_coords = []
        new_elts = []
        for elt, coord in zip(tmp_elts, sc):
            coord = map(roundclose, np.dot(cell_inv, coord))
            if any([( c >= 1 or c < 0 ) for c in coord]):
                continue
            new_coords.append(coord)
            new_elts.append(elt)
        new_coords = np.array(new_coords)

        new_coords %= 1.0
        new_coords %= 1.0
        self.set_natoms(len(new_coords))
        self.coords = new_coords
        self.atom_types = new_elts
        self.cell = new_cell
        return self

    def substitute(self, replace, rescale=True, in_place=False, **kwargs):
        """Replace atoms, as specified in a dict of pairs. 

        Keyword Arguments:
            rescale: 
                rescale the volume of the final structure based on the per 
                atom volume of the new composition.

            in_place: 
                change the species of the current Structure or return a new 
                one.

        Example:
            >>> s = io.read('POSCAR-Fe2O3')
            >>> s2 = s.substitute({'Fe':'Ni', 'O':'F'} rescale=True)
            >>> s2.substitute({'Ni':'Co'}, in_place=True, rescale=False)

        """

        if not in_place:
            new = self.copy()
            new.substitute(replace, rescale=rescale, in_place=False)
            return new

        volume = 0.0
        for atom in self:
            if atom.element_id in replace:
                atom.element_id = replace[atom.element_id]
            volume += atom.element.volume
        if rescale:
            self.set_volume(volume)
        self.set_composition()
        return self

    def refine(self, tol=1.0, recurse=True):
        """
        Identify atoms that are close to high symmetry sites (within `tol` and
        shift them onto them.

        Note: 
            "symprec" doesn't appear to do anything with spglib, so I am
            unable to get "loose" symmetry operations. Without which, this 
            doesn't work.

        Examples:
            >>> s = io.read('POSCAR')
            >>> s.symmetrize()
            >>> print s.spacegroup
            225L
            >>> s.refine()
            >>> print s.spacegroup
            1L

        """

        self.reduce()
        self.symmetrize(tol=1.0*tol)
        new_coords = []
        for atom in self:
            coords = []
            for rot, trans in self.operations:
                test = rot.dot(atom.coord) + trans
                test %= 1.0
                cart = np.dot(test, self.cell)
                if la.norm(cart-atom.cart_coord) < tol:
                    if not any([np.allclose(cart, c) for c in coords]):
                        coords.append(cart)
            central = np.average(coords, 0)
            new_coords.append(self.inv.T.dot(central))
        self.coords = new_coords
        if recurse:
            self.refine(tol=tol, recurse=False)

    def reduce(self, tol=1e-5, limit=1000, in_place=True):
        """
        Get the transformation matrix from unit to reduced cell
        Acta. Cryst. (1976) A32, 297
        Acta. Cryst. (2003) A60, 1

        Optional keyword arguments:
            *tol* : 
                eps_rel in Acta. Cryst. 2003 above. Similar to 
                tolerance for floating point comparisons. Defaults to 1e-5.
            *limit* : 
                maximum number of loops through the algorithm. Defaults to 
                1000. 
            *in_place* : 
                Change the Structure or return a new one. If True, the 
                transformation matrix is returned. If False, a tuple of
                (Structure, transformation_matrix) is returned. 

        Examples:
            >>> s = io.read('POSCAR')
            >>> s.reduce()
            >>> s.reduce(in_place=False, get_transform=False)

        """

        if not in_place:
            new = self.copy()
            trans = new.reduction(tol=tol, limit=limit)
            return new, trans

        # reduction parameters
        vectors = self.cell.copy()
        (a,b,c), (ksi,eta,zeta) = basis_to_niggli(vectors)
        trans = np.eye(3)

        # convergence variables
        _a, _b, _c = a*10, b*10, c*10
        mult = 10

        # tolerance and tests
        eps = tol * self.get_volume()**(1./3)

        def lt(x, y):
            return x < y - eps

        def gt(x, y):
            return x > y + eps

        def eq(x, y):
            return abs(x - y) < eps

        def update(mod, trans):
            trans = trans.dot(mod)
            return basis_to_niggli(trans.T.dot(vectors)), trans

        step = 0
        while step < limit:
            step += 1

            # N 1
            if gt(a,b) or (eq(a,b) and gt(abs(ksi),abs(eta))):
                r = np.array([[0,-1,0],[-1,0,0],[0,0,-1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 1')

            # N 2
            if gt(b, c) or ( eq(b,c) and gt(abs(eta),abs(zeta))):
                r = np.array([[-1,0,0],[0,0,-1],[0,-1,0]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 2')
                continue

            # N 3
            if gt(ksi*eta*zeta, 0):
                i = ( -1 if lt(ksi, 0) else 1 )
                j = ( -1 if lt(eta, 0) else 1 )
                k = ( -1 if lt(zeta, 0) else 1 )
                r = np.eye(3)*np.array([i,j,k])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 3 True path')
            else:
                vals = [1,1,1]
                p=0
                for i, x in enumerate([ksi, eta, zeta]):
                    if gt(x, 0):
                        vals[i] = -1
                    elif not lt(x, 0):
                        p = i
                if np.product(vals) < 0:
                    vals[p] = -1
                r = np.eye(3)*vals
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 3 False path')

                # test minimum reduction
            if ( mult*a + (a - _a) - (a*mult) == 0 
                    and 
                 mult*b + (b - _b) - (b*mult) == 0
                    and 
                 mult*c + (c - _c) - (c*mult) == 0 ):
                logger.debug('reduction: Minimum reduction test passed')
                break
            _a, _b, _c = a, b, c

            # N 5
            if (gt(abs(ksi), b) or 
                    (eq(ksi,b) and lt(2*eta,zeta)) or 
                    (eq(ksi,-b) and lt(zeta,0))):
                r = np.array([[1,0,0], [0,1,-sign(ksi)], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 5')
                continue

            # N 6
            if (gt(abs(eta),a) or 
                    ( eq(eta,a) and lt(2*ksi,zeta)) or 
                    ( eq(eta,-a) and lt(zeta,0))):
                r = np.array([[1,0,-sign(eta)], [0,1,0], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 6')
                continue
            
            # N 7
            if (gt(abs(zeta),a) or 
                    ( eq(zeta, a) and lt(2*ksi, eta)) or 
                    ( eq(zeta, -a) and lt(eta, 0))):
                r = np.array([[1,-sign(zeta),0], [0,1,0], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 7')
                continue

            # N 8
            if (lt(ksi + eta + zeta + a + b, 0) or 
                    (eq(ksi + eta + zeta + a + b, 0) and gt(2*(a+eta)+zeta, 0))):
                r = np.array([[1,0,1], [0,1,1], [0,0,1]])
                ((a,b,c),(ksi,eta,zeta)),trans = update(r, trans)
                logger.debug('reduction: test 8')
                continue
            break

        # temporarily stored transformations
        self._original_cell = self.cell.copy()
        self._unit_to_reduced = trans.T
        self._reduced_point_to_unit = trans
        self._unit_point_to_reduced = la.inv(trans)

        self.transform(trans.T)
        return trans

    def get_xrd(self, **kwargs):
        xrd = XRD(self)
        xrd.get_peaks()
        xrd.get_intensities()
        return xrd

    def get_pdf(self, **kwargs):
        return get_pdf(self, **kwargs)

class Prototype(models.Model):
    """
    Base class for a prototype structure. 

    Attributes:
        | composition
        | entry
        | name
        | structure

    """

    name = models.CharField(max_length=63, primary_key=True)
    structure = models.ForeignKey(Structure, related_name='+', 
                                  blank=True, null=True)
    composition = models.ForeignKey('Composition', blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'prototypes'

    @classmethod
    def get(cls, name):
        """
        Retrieves a :ref:`Prototype` named `name` if it exists. If not, creates
        a new one.

        Examples:
          >>> proto = Prototype.get('Corundum')

        """
        obj, new = cls.objects.get_or_create(name=name)
        if new:
            obj.save()
        return obj
