import numpy as np

import qmpy
from qmpy.utils import *
import symmetry.routines as routines

import logging

logger = logging.getLogger(__name__)

"""
Module to determine the necessary distortions for describing the full elastic
tensor for an arbitrary input Structure.

To do: need to convert the symmetry operations of a structure from the lattice
basis to cartesian.
"""


transforms = [ 
        [[0.1, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.1, 0.0],
         [0.0, 0.0, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.0, 0.1]],

        [[0.0, 0.0, 0.0],
         [0.1, 0.0, 0.0],
         [0.0, 0.0, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.1, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.1, 0.0, 0.0]]]

def get_unique_transforms(rotations):
    uniq_transforms = list(transforms)
