#!/usr/bin/env python

import numpy as np
import numpy.linalg as la
import itertools
import random
import logging

import matplotlib.pylab as plt

logger = logging.getLogger(__name__)

class Region:
    def __init__(self, phases):
        self.space = set.union(*[p.space for p in phases ])
        cc = [ [p.unit_comp[e] for e in self.space ] for p in phases ]
        self.ref_c = np.array(cc)
        self.ref_e = np.array([[p.energy] for p in phases ])
        order = np.lexsort(self.ref_c.T)
        self.ref_c = self.ref_c[order]
        self.ref_e = self.ref_e[order]
        self._inv = None
        self.contained = []
        self.rel_c = None
        self.rel_e = None

    def contains(self, point):
        """
        Put the point in barycentric coordinates and check that it is in the
        simplex.

        """
        coord = self.gbc(point)
        return all( a >= 0 for a in coord ) and sum(coord) <= 1

    @property
    def inv(self):
        if self._inv is None:
            normed = self.points[1:] - self.points[0].T
            self._inv = la.inv(normed).T
        return self._inv

    def get_barycentric_coordinate(self, point):
        r = np.array(rel_c) - self.rel_c[0]
        return np.dot(self.inv, r)

    def gbc(self, point):
        return self.get_barycentric_coordinate(point)

    def compute_rel_e(self):
        energies = np.array([ p.energy for p in self.contained ])
        self.rel_e = energies - np.dot(self.rel_c, self.ref_e)

def get_relative_energy(point, references):
    p, e = point

    ref_e, ref_p = references
    simplex = Simplex(ref_p)
    coord = simplex.gbc(p)
    return e - np.dot(coord, ref_e)

def discard_contained(points, energies, references):
    points = np.array(points)
    simplex = Simplex([p + [e] for p, e in references ])
    discard = np.zeros(points.shape)

    for i, (p, e) in enumerate(zip(points, energies)):
        discard[i] = simplex.contains(p+[e])
    return discard

def make_binhull(points, energies):
    points = np.array(points)
    energies = np.array(energies)

    points = points[energies<0]
    energies = energies[energies<0]
    bottom = np.argsort(energies)[0]

    init_p = [[0], [1], [points[b]]]
    init_e = [0, 0, energies[b]]

    discard = discard_contained(points, energies, (init_p, init_e))
    points = points[not discard]
    energies = energies[not discard]

    dists = np.zeros(energies.shape)
    for facet in refs:
        for p, e in zip(points, energies):
            print p, e


def test():
    dims = 2
    points = [ [ random.random() for i in range(dims) ] for j in range(dims+1) ]
    s = Simplex(points)
    p2 = np.average(s.points, 0)

    plt.plot(s.points[:,0], s.points[:,1], 'ro')
    for p1, p2 in s.facets:
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k--')

    inside = []
    outside = []
    for i in range(100):
        p1 = [ random.random() for i in range(dims) ]
        if s.contains(p1):
            inside.append(p1)
        else:
            outside.append(p1)
    inside = np.array(inside)
    outside = np.array(outside)
    plt.plot(inside[:, 0], inside[:,1], 'bo')
    plt.plot(outside[:, 0], outside[:,1], 'go')

    plt.show()

if __name__ == '__main__':
    phases = [ [random.random()] for i in range(100) ]
    energies = [ -10*random.random() + 5 for i in range(100) ]

    make_binhull(points, energies)
