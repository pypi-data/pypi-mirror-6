import numpy as np
import numpy.linalg as linalg
import itertools
from collections import defaultdict
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

#__all__ = ['get_pdf']

def get_pair_distances(structure, max_dist=10):
    """
    Loops over pairs of atoms that are within radius max_dist of one another.
    Returns a dict of (atom1, atom2):[list of distances].

    """
    dists = []

    lat_params = structure.lat_params
    limits = [ int(np.ceil(max_dist/lat_params[i])) for i in range(3) ]
    new_struct = structure.transform([ l+1 for l in limits ], in_place=False)
    new_struct.reduce()
    new_struct.symmetrize()

    pairs = list(itertools.combinations(structure.comp.keys(), r=2))
    dists = defaultdict(list)
    for a1 in new_struct.uniq_sites:
        e1 = a1.label
        for a2 in new_struct.atoms:
            e2 = a2.element_id
            dist = new_struct.get_distance(a1, a2)
            if dist < 1e-3:
                continue
            dists[frozenset([e1,e2])] += [dist]*a1.multiplicity
    return dists

def get_pdf(structure, max_dist=5, smearing=0.1):
    """

    """
    distances = get_pair_distances(structure, max_dist=max_dist)
    elts = list(set([ a.element_id for a in structure ]))
    rhos = dict((elt, structure.comp[elt]/structure.get_volume()) for elt in elts)

    renderer = Renderer()

    xs = np.mgrid[0:max_dist:100j]
    dr = xs[1] - xs[0]
    ideals = dict((elt, 4.0*np.pi*rhos[elt]/3.0) for elt in elts)

    for pair, dists in distances.items():
        pair = list(pair)
        if len(pair) == 1:
            pair *= 2
        e1, e2 = pair

        vals = np.zeros(xs.shape)
        prefactor = 1.0/(smearing*np.sqrt(2*np.pi))
        norms = [ ( (x+dr/2)**3 - (x-dr/2)**3) for x in xs ]
        for d in dists:
            if d < 0.5:
                continue
            vals += np.exp(-(d-xs)**2/(2*smearing**2))
            #vals += prefactor*np.exp(-(d-xs)**2/(2*smearing**2))
        vals = vals/norms
        vals = [ v if v > 1e-4 else 0.0 for v in vals ]
        line = Line(zip(xs, vals), label='%s-%s' % (e1, e2))
        renderer.add(line)

    renderer.xaxis.label = 'interatomic distance [$\\AA$]'
    return renderer
