import numpy as np
import numpy.linalg as linalg
import itertools
from collections import defaultdict
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

#__all__ = ['get_pdf']

class PDF(object):
    """
    Container class for a Pair-distribution function.

    Attributes:
        structure: :mod:`~qmpy.Structure`
        pairs: dict of (atom1, atom2):[distances]
        limit: maximum distance
    """

    def __init__(self, structure, limit=6):
        elements = structure.comp.keys()
        pairs = itertools.product(elements, elements)
        self.pairs = [ self.get_pair(pair) for pair in pairs ]
        self.distances = dict((p, []) for p in self.pairs)
        self.weights = dict((p, []) for p in self.pairs)
        self.sites = list(structure.uniq_sites)
        self.limit = limit
        if limit:
            # make a structure large enough to contain all atoms `limit` away
            # structure.reduce()
            lp = structure.lat_params
            limits = [ int(np.ceil(limit/lp[i])) for i in range(3) ]
            self.structure = structure.t([ l+1 for l in limits], in_place=False)
        else:
            self.structure = structure.copy()

    def get_pair(self, pair):
        return tuple(sorted(pair))

    def get_pair_distances(self):
        """
        Loops over pairs of atoms that are within radius max_dist of one another.
        Returns a dict of (atom1, atom2):[list of distances].

        """
        for s1 in self.sites:
            c1 = self.structure.inv.T.dot(s1.cart_coord)
            for a2 in self.structure.atoms:
                dist = self.structure.get_distance(c1, a2, wrap_self=False)
                # returns None if distance is greater than limit
                if dist is None:
                    continue
                if self.limit:
                    if dist > self.limit:
                        continue
                if abs(dist) < 0.001:
                    dist = min(self.structure.lat_params[:3])

                for a1 in s1.atoms:
                    pair = self.get_pair((a1.element_id, a2.element_id))
                    self.distances[pair] += [dist]
                    w = s1.multiplicity*a1.occupancy*a2.occupancy
                    self.weights[pair] += [float(w)]

    def plot(self, smearing=0.1):
        renderer = Renderer()
        xs = np.mgrid[0:self.limit:1000j]
        dr = xs[1] - xs[0]
        for pair in self.pairs:
            e1, e2 = pair

            vals = np.zeros(xs.shape)
            prefactor = 1.0/(smearing*np.sqrt(2*np.pi))
            norms = [ ( (x+dr/2)**3 - (x-dr/2)**3) for x in xs ]
            for w, d in zip(self.weights[pair], self.distances[pair]):
                if not d:
                    continue
                vals += np.exp(-(d-xs)**2/(2*smearing**2))*w
            vals = vals/norms
            vals = [ v if v > 1e-4 else 0.0 for v in vals ]
            line = Line(zip(xs, vals), label='%s-%s' % (e1, e2))
            renderer.add(line)

        renderer.xaxis.label = 'interatomic distance [$\\AA$]'
        return renderer
