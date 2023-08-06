# qmpy/materials/atom.py

"""
The Atom and Site models represent a single atom or an atomic site,
repsectively. 

"""

from numpy.linalg import solve, norm
import time
import copy
from collections import defaultdict
import logging

from django.db import models

import qmpy
from qmpy.utils import *
from qmpy.analysis.symmetry import WyckoffSite

logger = logging.getLogger(__name__)

class AtomError(qmpy.qmpyBaseError):
    pass

class SiteError(qmpy.qmpyBaseError):
    pass

class Atom(models.Model):
    """
    Model for an Atom.

    Relationships:
        | :mod:`~qmpy.Structure` via structure
        | :mod:`~qmpy.Element` via element
        | :mod:`~qmpy.Site` via site 
        | :mod:`~qmpy.Wyckoff` via wyckoff

    Attributes:
        | id
        | x, y, z: Coordinate of the atom
        | direct: Is coordinate in fractional coordinates or cartesian
        | fx, fy, fz: Forces on the atom
        | magmom: Magnetic moment on the atom (in &Mu;<sub>b</sub>)
        | occupancy: Occupation fraction (0-1).
        | ox: Oxidation state of the atom (can be different from charge)
        | charge: Charge on the atom
        | volume: Volume occupied by the atom

    """
    structure = models.ForeignKey('Structure', related_name='atom_set',
                                               null=True)
    site = models.ForeignKey('Site', related_name='atom_set', null=True)

    # species
    element = models.ForeignKey('Element', blank=True, null=True)
    ox = models.IntegerField(default=None, blank=True, null=True)

    # position
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    direct = models.BooleanField(default=True)

    # forces
    fx = models.FloatField(blank=True, null=True)
    fy = models.FloatField(blank=True, null=True)
    fz = models.FloatField(blank=True, null=True)

    # properties
    magmom = models.FloatField(blank=True, null=True)
    charge = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)

    # symmetry
    occupancy = models.FloatField(default=1)
    wyckoff = models.ForeignKey(WyckoffSite, blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'atoms'

    def __str__(self):
        return '%s @ %3f %3f %3f' % (self.element_id, 
                self.x, self.y, self.z)

    def __eq__(self, other):
        if self.element_id != other.element_id:
            return False
        try:
            if any(abs(self.cart_coord - other.cart_coord) > 5e-1):
                return False
        except:
            if any(abs(self.coord - other.coord) > 1e-3):
                return False
        return True

    def __cmp__(self, other):
        comp_arr = [[ self.x, other.x ],
                    [ self.y, other.y ],
                    [ self.z, other.z ],
                    [ self.ox, other.ox ],
                    [ qmpy.elements[self.element_id]['z'], 
                      qmpy.elements[other.element_id]['z'] ]]
        comp_arr = np.array([ row for row in comp_arr if 
                                  all( not x is None for x in row ) ]).T
        if len(comp_arr) == 0:
            raise AtomError

        if all(abs(comp_arr[0] - comp_arr[1]) < 1e-3):
            return 0
        ind = np.lexsort(comp_arr.T)
        return 2*ind[0] - 1

    @property
    def forces(self):
        """Forces on the Atom in [x, y, z] directions."""
        return np.array([self.fx , self.fy, self.fz])

    @forces.setter
    def forces(self, values):
        self.fx, self.fy, self.fz = values

    @property
    def coord(self):
        """[x,y,z] coordinates."""
        return np.array([self.x, self.y, self.z])

    @coord.setter
    def coord(self, values):
        self.x, self.y, self.z = values

    @property
    def cart_coord(self):
        """Cartesian coordinates of the Atom."""
        if self.direct is True and self.structure is None:
            raise AtomError("Cannot determine cartesian coordinate")
        elif self.direct:
            return np.dot(self.coord, self.structure.cell)
        else:
            return self.coord

    @cart_coord.setter
    def cart_coord(self, value):
        if self.structure is None:
            self.coord = value
            self.direct = False
        else:
            coords = self.structure.inv.T.dot(value)
            self.coord = coords

    @property
    def species(self):
        """Formatted Species string. e.g. Fe3+, O2-"""
        return format_species(self.element_id, self.ox)

    @property
    def index(self):
        """
        None if not in a :Structure:, otherwise the index of the atom 
        in the structure.
        """
        if not self.structure: 
            return None
        return self.structure.atoms.index(self)

    @classmethod
    def create(cls, element, coord, **kwargs):
        """
        Creates a new Atom object. 

        Arguments:
            element (str or Element): Specifies the element of the Atom.
            coord (iterable of floats): Specifies the coordinate of the Atom.

        Keyword Arguments:
            direct: 
                True if `coord` contains fractional coordinates, False if 
                `coord` contains cartesian coordinates.
            forces: 
                Specifies the forces on the atom.
            magmom: 
                The magnitude of the magnetic moment on the atom.
            charge: 
                The charge on the Atom.
            volume: 
                The atomic volume of the atom (Angstroms^3).

        Examples::
            >>> Atom.create('Fe', [0,0,0])
            >>> Atom.create('Ni', [0.5, 0.5, 0.5], ox=2, magmom=5, 
            >>>                                 forces=[0.2, 0.2, 0.2],
            >>>                                 volume=101, charge=1.8,
            >>>                                 occupancy=1)

        """
        atom = Atom()
        atom.element_id = element
        atom.coord = coord
        valid_keys = ['ox', 'occupancy', 'wyckoff', 'charge', 
                'magmom', 'volume', 'forces', 'direct']
        for key in valid_keys:
            if key in kwargs:
                setattr(atom, key, kwargs[key])
        return atom

    def copy(self):
        """
        Creates an exact copy of the atom, only without the matching primary
        key.

        Examples::

            >>> a = Atom.get('Fe', [0,0,0])
            >>> a.save()
            >>> a.id
            1
            >>> a.copy()
            >>> a
            <Atom: Fe - 0.000, 0.000, 0.000>
            >>> a.id
            None
        
        """
        atom = Atom()
        atom.element_id = self.element_id
        atom.coord = self.coord
        valid_keys = ['ox', 'occupancy', 'charge', 
                'magmom', 'volume', 'forces']
        for key in valid_keys:
            setattr(atom, key, getattr(self, key))
        return atom

    def as_site(self):
        s = Site()
        s.coord = self.coord
        s.atoms = [self]
        return s

    def is_on(self, site, tol=1e-5):
        """
        Tests whether or not the ``Atom`` is on the specified ``Site``.

        Examples::
            >>> a = Atom.create('Fe', [0,0,0])
            >>> s = a.as_site()
            >>> a2 = Atom.create('Ni', [0,0,0])
            >>> a2.is_on(s)
            True
        """
        vec = self.coord - site.coord
        dist = norm(np.dot(vec - np.round(vec), self.structure.cell))
        return dist < tol

class Site(models.Model):
    """
    A lattice site. 

    A site can be occupied by one Atom, many Atoms or no Atoms. 

    Relationships:
        | :mod:`~qmpd.Structure` via structure
        | :mod:`~qmpy.Atom` via atom_set
        | :mod:`~qmpy.Wyckoff` via wyckoff

    Attributes:
        | id
        | x, y, z: Coordinate of the Site

    """
    structure = models.ForeignKey('Structure', blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    wyckoff = models.ForeignKey(WyckoffSite, blank=True, null=True)

    class Meta:
        app_label = 'qmpy'
        db_table = 'sites'

    def __str__(self):
        coord_str = ''
        comp_str = ''
        if not self.coord is None:
            coord_str = '%0.3f %0.3f %0.3f' % tuple(self.coord)

        if len(self.atoms) == 1:
            comp_str = self.atoms[0].element_id
        elif len(self.atoms) > 1:
            elts = [ str(a.element) for a in self.atoms ]
            specs = [ str(a.species) for a in self.atoms ]
            if ( len(set(elts)) == len(set(specs)) and 
                    len(set([ a.ox for a in self.atoms ])) == 1):
                comp_str = '('+','.join(elts)+')'
            else:
                comp_str = '('+','.join(specs)+')'

        if coord_str and comp_str:
            return "%s @ %s" % (comp_str, coord_str)
        elif coord_str:
            return 'Vac @ %s' % (coord_str)
        elif comp_str:
            return comp_str

    def __eq__(self, other):
        if not self.comp == other.comp:
            return False
        try:
            if any(abs(self.cart_coord - other.cart_coord) > 1e-3):
                return False
        except:
            if any(abs(self.coord - other.coord) > 1e-5):
                return False
        return True

    def __getitem__(self, i):
        return self.atoms[i]

    def __len__(self):
        return len(self.atoms)

    _atoms = None
    @property
    def atoms(self):
        """List of Atoms on the Site."""
        if self._atoms is None:
            if self.id is None:
                self._atoms = []
            else:
                self._atoms = list(self.atom_set.all())
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        if isinstance(atoms, Atom):
            self._atoms = [atoms]
        elif all([ isinstance(a, Atom) for a in atoms ]):
            self._atoms = atoms
        else:
            raise TypeError('atoms must be a sequence of Atoms')

    @property
    def coord(self):
        """[Site.x, Site.y, Site.z]"""
        if any([ self.x is None, self.y is None, self.z is None]):
            return None
        return np.array(map(float,[self.x, self.y, self.z]))

    @coord.setter
    def coord(self, values):
        self.x, self.y, self.z = values

    @property
    def cart_coord(self):
        """
        Returns:
          length 3 array of floats. The positions of the Site in cartesian
          coordinates.

        Raises:
          SiteError: If the Site coordinates are direct, and the Site is 
          not associated with a structure, cartesian coordinates cannot 
          be determined, so a SiteError is raised.

        """
        if self.structure is None:
            raise SiteError("Cannot determine cartesian coordinate")
        return np.dot(self.coord, self.structure.cell)

    @cart_coord.setter
    def cart_coord(self, value):
        if self.structure is None:
            self.coords = value
            self.direct = False
            return
        coords = self.structure.inv.T.dot(value)
        self.coords = coords
    
    @property
    def label(self):
        """
        Assigns a human friendly label for the Site, based on its atomic
        composition. If singly occupied, returns the symbol of the atom on the
        site. If multiply occupied, returns a comma seperated string

        Examples:
            >>> a1 = Atom.create('Fe', [0,0,0], occupancy=0.2)
            >>> a2 = Atom.create('Ni', [0,0,0], occupancy=0.8)
            >>> s = Site.from_atoms([a1,a2])
        """
        if len(self.atoms) == 1:
            return self.atoms[0].element_id
        else:
            elts = [ str(a.element) for a in self.atoms ]
            specs = [ str(a.species) for a in self.atoms ]
            if len(set(elts)) == len(set(specs)):
                comp_str = '('+','.join(elts)+')'
            else:
                comp_str = '('+','.join(specs)+')'
            return comp_str

    @classmethod
    def from_atoms(cls, atoms, tol=1e-4):
        """
        Constructs a Site from an iterable of Atoms.

        Notes:
          Site.coord is set as the average coord of all assigned Atoms.

          Checks that the Atoms are close together. If the Atoms are further
          apart than `tol`, raises a SiteError

        Arguments:
          atoms (iterable of `Atom`): List of Atoms to occupy the Site.

        Keyword Arguments:
          tol (float): Atoms must be within `tol` of each other to be assigned 
          to the same Site. Defaults to 1e-4.

        Examples:
        >>> a1 = Atom.create('Fe', [0,0,0])
        >>> a2 = Atom.create('Ni', [1e-5, -1e-5, 0])
        >>> s = Site.from_atoms([a1,a1])
        """
        site = cls()
        if isinstance(atoms, Atom):
            site.coord = atoms.coord
            site.atoms = [atoms]
            return site

        site.coord = atoms[0].coord
        for a in atoms:
            site.add_atom(a)
        return site

    @classmethod
    def create(cls, coord=None, comp=None):
        """
        Constructs a Site from a coordinate.

        Note:
          The Site is created without any Atoms occupying it.

        Keyword Arguments:
          coord (length 3 iterable): Assigns the x, y, and z coordinates of 
            the Site.
          comp (dict, string, or qmpy.Element): Composition dictionary.
           Flexible about input forms. Options include: <Element: Fe>, 'Fe',
           {"Fe":0.5, "Co":0.5}, and {<Element: Ni>:0.5, <Element: Co>:0.5}.

        Raises:
            TypeError: if `comp` isn't a string, ``Atom``, ``Element``.

        Examples:
        >>> s = Site.create([0.5,0.5,0.5])
        """
        site = cls()
        site.coord = coord
        if comp:
            if isinstance(comp, qmpy.Element):
                a = Atom.create(comp.symbol, coord)
                site.add_atom(a)
            elif isinstance(comp, str):
                a = Atom.create(comp, coord)
                site.add_atom(a)
            elif isinstance(comp, Atom):
                site.add_atom(comp)
            elif isinstance(comp, dict):
                for k,v in comp.items():
                    a = Atom.create(k, coord, occupancy=v)
            else:
                raise TypeError("Unknown datatype")
        return site

    @property
    def comp(self):
        """
        Composition dictionary of the Site.

        Returns:
          dict: of (element, occupancy) pairs. 
        
        Examples:
        >>> a1 = Atom('Fe', [0,0,0], occupancy=0.2)
        >>> a2 = Atom('Ni', [0,0,0], occupancy=0.8)
        >>> s = Site.from_atoms([a1,a2])
        >>> s.comp
        {'Fe':0.2, 'Ni':0.8}

        """
        comp = defaultdict(float)
        for a in self.atoms:
            comp[a.element_id] += a.occupancy
        return dict(comp)

    def add_atom(self, atom, tol=1e-3):
        """
        Adds Atom to `Site.atoms`. 

        Notes:
          Tests whether the `atom` belongs to different Structure and if it is
          within `tol` of the Site.

          If the Site being assigned to doens't have a coordinate, it is assigned
          the coordinate of `atom`.

        Arguments:
          atom (Atom): Atom to add to the structure.

        Keyword Arguments:
          tol (float): Distance between `atom` and the Site for the Atom to be 
            assigned to the Site. Raises a SiteError if the distance is 
            greater than `tol`. 

        Raises:
          SiteError: If `atom` is more than `tol` from the Site. 

        Examples:
        >>> s = Site.create([0,0,0])
        >>> a = Atom.create('Fe', [0,0,0])
        >>> s.add_atom(a)
        >>> s2 = Site()
        >>> s2.add_atom(a)

        """
        if not self.coord is None:
            if any(abs(atom.coord - self.coord) > tol):
                raise SiteError("%s is too far from %s to add" % (atom, self))
            else:
                self.atoms.append(atom)
        else:
            self.coord = atom.coord
            self.atoms = [atom]

    def full(self, tol=1e-3):
        """
        Evaluates whether the Site is fully occupied.

        Returns:
          bool: True if the sum of the occupancies of all atoms on the site 
          is within `tol` of 1.

        """
        return ( abs(sum(self.comp.values()) - 1) < tol)

    def magmom(self):
        """
        Calculates the composition weighted average magnetic moment of the atoms 
        on the Site.

        Returns:
          float or None
        """
        if self.atoms:
            mag = sum([ a.magmom*a.occupancy for a in self.atoms ])
            return mag/self.occupancy()

    @property
    def ox(self):
        """
        Calculates the composition weighted average oxidation state of the atoms 
        on the Site.

        Returns:
          float or None

        """
        if self.atoms:
            ox = sum([ a.ox*a.occupancy for a in self.atoms ])
            return ox/self.occupancy()

    def occupancy(self):
        """
        Calculates the total occupancy of the site.

        Returns:
          float or None
        """
        if self.atoms:
            return sum([ a.occupancy for a in self.atoms ])

