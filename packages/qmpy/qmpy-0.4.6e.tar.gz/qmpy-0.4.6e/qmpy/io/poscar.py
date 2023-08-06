#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import logging
import gzip
import os
from os.path import exists, isfile, isdir
import time

from django.db import models
import numpy as np

import qmpy
import qmpy.materials.structure as st
import qmpy.materials.composition as comp
import qmpy.data.meta_data as ref
from qmpy.utils import *

logger = logging.getLogger(__name__)

class POSCARError(Exception):
    pass

def write(struct, filename=None, direct=True, distinct_by_ox=False, 
                  vasp4=False, **kwargs):
    comp = struct.comp
    struct.atoms = atom_sort(struct.atoms)

    cdict = defaultdict(int)
    if not distinct_by_ox:
        ordered_keys = sorted(comp.keys())
        for a in struct:
            cdict[a.element_id] += 1
        counts = [ int(cdict[k]) for k in ordered_keys ]
    else:
        for a in struct.atoms:
            if int(a.oxidation_state) != a.oxidation_state:
                cdict['%s%+f' % (a.element_id, a.oxidation_state)] += 1
            else:
                cdict['%s%+d' % (a.element_id, a.oxidation_state)] += 1
        ordered_keys = sorted([ k for k in cdict.keys() ])
        counts = [ int(cdict[k]) for k in ordered_keys ]

    poscar = ' '.join(set(a.element_id for a in struct.atoms)) + '\n 1.0\n'
    cell = '\n'.join([ ' '.join([ '%f' % v  for v in vec ]) for vec in
        struct.cell ])
    poscar += cell +'\n'
    names = ' '.join( a for a in ordered_keys ) + '\n'
    ntypes = ' '.join( str(n) for n in counts ) + '\n'
    if not vasp4:
        poscar += names
    poscar += ntypes
    if direct:
        poscar += 'direct\n'
        for x,y,z in struct.coords:
            poscar += ' %.10f %.10f %.10f\n' % (x,y,z)
    else:
        poscar += 'cartesian\n'
        for x, y, z in struct.cartesian_coords:
            poscar += ' %.10f %.10f %.10f\n' % (x,y,z)

    if filename:
        open(filename, 'w').write(poscar)
    else:
        return poscar

def read(poscar, species=None):
    """
    Read a POSCAR format file.

    Reads VASP 4.x and 5.x format POSCAR files.

    Keyword Arguments:
        `species`:
            If the file is 4.x format and the title line doesn't indicate what
            species are present, you must supply them (in the correct order)
            with the `species` keyword.

    Raises:
        POSCARError: If species data is not available.
    """
    struct = st.Structure()
    poscar = open(poscar,'r')
    title = poscar.readline().strip()
    scale = float(poscar.readline().strip())
    s = float(scale)
    cell = [[ float(v) for v in poscar.readline().split() ],
            [ float(v) for v in poscar.readline().split() ],
            [ float(v) for v in poscar.readline().split() ]]
    cell = np.array(cell)

    if s > 0:
        struct.cell = cell*s
    else:
        struct.cell = cell
        struct.volume = -1*s

    vasp5 = False
    _species = poscar.readline().strip().split()
    try:
        float(_species[0])
    except:
        vasp5 = True
        counts = [ int(v) for v in poscar.readline().split() ]
    if not vasp5:
        counts = map(int, _species)
        if not species:
            _species = title.strip().split()
            for s in _species:
                if not s in qmpy.elements.keys():
                    msg = 'In VASP4.x format, title line MUST be species present'
                    raise POSCARError
        else:
            _species = species
    species = _species

    atom_types = []
    for n,e in zip(counts, species):
        atom_types += [e]*n

    style = poscar.readline()
    direct = False
    if style[0] in ['D', 'd']:
        direct = True

    struct.natoms = sum(counts)
    struct.ntypes = len(counts)
    composition = defaultdict(float)
    atoms = []
    inv = np.linalg.inv(cell).T
    for i in range(struct.natoms):
        atom = st.Atom()
        atom.element_id = atom_types[i]
        if direct:
            atom.coord = [ float(v) for v in poscar.readline().split() ]
        else:
            cart = [ float(v) for v in poscar.readline().split() ]
            atom.coord = np.dot(inv, cart)
        atom.direct = True
        atoms.append(atom)
        composition[atom_types[i]] += 1
    struct.atoms = atoms
    struct.composition = comp.Composition.get(composition)
    struct.reported_composition = comp.Composition.get(composition)
    struct.get_volume()
    return struct
