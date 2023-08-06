#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import numpy.linalg as linalg
from scipy.spatial import Delaunay, Voronoi
import matplotlib.pylab as plt
import itertools
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

def get_facet_area(vertices):
    area = 0
    vertices = vertices[np.lexsort(vertices.T)]
    if not vertices.shape[1] == 3:
        raise ValueError('vertices must be an Nx3 array')
    for i in range(len(vertices)-2):
        a = vertices[i]
        b = vertices[i+1]
        c = vertices[i+2]
        ab = b-a
        ac = c-a
        area += linalg.norm(np.cross(ab, ac))
    return area

def find_closest(structure, max_dist=5, tol=2e-1):
    """ Based on the following algorithm defines a list of pairs of atoms,
    sotred as a tuple, of the form (atom1,atom2,dist_1_2). For all triplets
    of atoms A, B and C, the atoms A and B are neighbors if and only if:
        AB is shorter than AC
        and
        AB is shorter than BC
    """
    lat_params = structure.lat_params
    limits = [ int(np.ceil(max_dist/lat_params[i])) for i in range(3) ]
    limits = np.array(limits) + 1
    new_struct = structure.transform(limits, in_place=False)
    distances = np.zeros((structure.natoms, structure.natoms*np.product(limits)))

    for i, j in itertools.product(range(structure.natoms),
                                  range(new_struct.natoms)):
        dist = new_struct.get_distance(i,j)
        if abs(dist) < 0.01:
            dist = structure.minimum_repeat_distance
        distances[i,j] = dist

    nns = {}
    for i, a in enumerate(structure.atoms):
        a.neighbors = []
        dists = np.array(distances[i])
        dists /= min([d for d in dists ])
        inds = np.ravel(np.argwhere((dists - 1)<tol))
        inds = np.array([ ii for ii in inds if ii != i ])
        inds %= structure.natoms
        a.neighbors = [ structure[j] for j in inds ]
        nns[a] = a.neighbors
    return nns

def find_neighbors(structure, max_dist=8, tol=1.0):
    lps = structure.lat_params
    limits = np.array([ int(np.ceil(max_dist/lps[i])) for i in range(3)])
    new_struct = structure.transform(limits+1, in_place=False)
    new_struct.symmetrize()

    nns = {}
    for atom in new_struct.uniq_atoms:
        new_struct.recenter(atom)
        tess = Voronoi(new_struct.cartesian_coords)
        nn = defaultdict(list)
        for j, r in enumerate(tess.ridge_points):
            if not i in r:
                continue
            inds = tess.ridge_vertices[j]
            verts = tess.vertices[inds]
            area = get_facet_area(verts)
            other_atom = [k for k in tess.ridge_points[j] if k != i ][0]
            nn[area].append(other_atom % structure.natoms)
        b = max(nn.keys())
        neighbors = []
        for k, v in nn.items():
            if k < tol:
                continue
            neighbors += v
        nns[atom] = list([ structure[k] for k in neighbors])
        atom.neighbors = nns[atom]
    return nns
