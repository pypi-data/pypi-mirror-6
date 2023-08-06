import numpy as np
import logging

import qmpy
from qmpy.utils import *

logger = logging.getLogger(__name__)

"""
Module for identifying likely orderings on a lattice. Useful for identifying
antiferromagnetic orderings, as well as site occupancy. At present, it can only
handle mixing of two species
"""

def find_ordering(structure):
    raise NotImplementedError

if __name__ == '__main__':
    s = io.read(INSTALL_PATH+'/io/files/POSCAR_BCC')
    sl = sc.get_spin_lattice(supercell=[5,5,5])

    sl.run_MC()

