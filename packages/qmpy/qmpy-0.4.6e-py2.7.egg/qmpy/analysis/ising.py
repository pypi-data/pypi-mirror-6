import networkx as nx
import itertools
import numpy as np
import matplotlib.pylab as plt
import matplotlib.animation as animation
import random
import logging

import qmpy
from qmpy.utils import *


logger = logging.getLogger(__name__)

__all__ = ['LatticePoint', 'SpinLattice']

class LatticePoint:
    def __init__(self, position, spin=None):
        self.coord = position
        self.spin = spin

    def __str__(self):
        return '(%s)' % (''.join([ '%g' % c for c in self.coord ]))

    def __repr__(self):
        return '<LatticePoint %s>' % (self.__str__())

    @staticmethod
    def from_atom(atom):
        self.coord = atom.coord
        self.spin = atom.spin

class SpinLattice:
    spin_states = 2
    temperature = 20
    steps = 100

    def __init__(self, pairs):
        self.graph = nx.MultiGraph()
        self.graph.add_edges_from(pairs)
        self.lattice_points = self.graph.nodes()
        self.pairs = self.graph.edges()
        
        self.interaction = -1
        self.field = 0
        self.energy = None

    def __len__(self):
        return len(self.lattice_points)

    def __getitem__(self, index):
        return self.lattice_points[index]

    @staticmethod
    def create_2d(n):
        nodes = []
        edges = []
        for i in range(n):
            row = []
            for j in range(n):
                lp = LatticePoint([i,j])
                row.append(lp)
            nodes.append(row)
        nodes = np.array(nodes)
        
        for i in range(n):
            for j in range(n):
                edges.append((nodes[i,j], nodes[(i-1)%n, j]))
                edges.append((nodes[i,j], nodes[(i+1)%n, j]))
                edges.append((nodes[i,j], nodes[i,(j-1)%n]))
                edges.append((nodes[i,j], nodes[i,(j+1)%n]))

        sl = SpinLattice(edges)
        sl.square_lattice = nodes
        return sl

    @property
    def up_spins(self):
        return [ s for s in self if s.spin == 1 ]

    @property
    def fraction(self):
        return len(self.up_spins)/float(len(self))

    def set_fraction(self, fraction, max_size=100):
        for s in self:
            s.spin = -1

        upper = np.ceil(fraction*len(self))
        lower = np.floor(fraction*len(self))
        du = upper/float(len(self)) - fraction
        dl = lower/float(len(self)) - fraction
        if abs(du) <= abs(dl):
            t = upper
        else:
            t = lower

        for i in range(int(t)):
            self[i].spin = 1


    def compute_total_lattice_energy(self):
        """
        Compute the total energy of the lattice using the Ising model
        hamiltonian:

        H(s) = -J * sum_{i, j}( s_i * s_j )

        So, for a positive interaction, J, the energy is minimized when all
        pairs are alike. Likewise, when J is negative, the enegy is minimized
        when all pairs are unlike.
        """

        energy = 0
        for lp1, lp2 in self.pairs:
            if lp1.spin == lp2.spin:
                energy -= self.interaction
            else:
                energy += self.interaction
        self.energy = energy/2.0
        return self.energy

    def randomize_spins(self):
        for lp in self.lattice_points:
            lp.spin = 1
            if random.random() > 0.5:
                lp.spin *= -1
        self.energy = None

    def attempt_flip(self):
        """
        Randomly selects a lattice point, and attempts to flip it.

        dE = 2*J*sum(neighboring spins)
        """
        lp1 = random.choice(self.lattice_points)
        de = 2*J*sum([ lp2.spin for lp2 in self.graph[lp1] ])
        if de > 0 and np.exp(-self.temperature*de) < random.random():
            return
        else:
            self.energy += de
            lp.spin *= -1

    def attempt_swap(self, accept=True):
        lp1 = random.choice(self.lattice_points)
        lp2 = random.choice(self.lattice_points)

        if lp1.spin == lp2.spin:  # no self swaps
            return self.attempt_swap()

        de = J*sum([ lp3.spin for lp3 in self.graph[lp1] 
                                     if not lp3 == lp2 ])
        de += J*sum([ lp3.spin for lp3 in self.graph[lp2] 
                                     if not lp3 == lp1 ])
        if de > 0 and np.exp(-self.temperature*de) < random.random():
            return
        else:
            self.energy += de
            lp1.spin *= -1
            lp2.spin *= -1

    def run_GCMC(self, mu=0):
        """
        Run Monte Carlo in the Grand Canonical Ensemble. 

        Examples:
        >>> sl = SpinLattice.create_2d(10)
        >>> sl.run_GCMC()
        >>> sl.run_GCMC(-1)
        >>> sl.run_GCMC(1)
        """
        
        steps = self.steps * len(self.lattice_points)

        self.randomize_spins()
        self.energies = np.zeros(steps)
        for i in range(steps):
            self.attemp_flip()
            self.energies[i] = self.energy

    def run_MC(self, x=0.5):
        """
        Run Monte Carlo in the Canonical Ensemble
        
        Examples:
        >>> sl = SpinLattice.create_2d(10)
        >>> sl.run_MC()
        >>> sl.run_MC(0.1)
        >>> sl.run_MC(0.25)
        """
        steps = self.steps * len(self.lattice_points)

        self.set_fraction(x)

        self.energy = self.compute_total_lattice_energy()
        energies = np.zeros(steps)

        for i in range(steps):
            self.attempt_swap()
            self.energies[i] = self.energy

def plot(self):
    #f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    fig = plt.figure()
    #plt.imshow(squarray, interpolation='nearest')
    grid = np.array(self.init_grid)
    im = plt.imshow(grid, interpolation='nearest')
    flips = list(self.flips)
    
    def run(*args):
        while True:
            flip = flips.pop(0)
            if flip is None:
                continue
            grid[flip.coord[0], flip.coord[1]] *= -1
            im.set_array(grid)
            return im,
        
    ani = animation.FuncAnimation(fig, run, interval=5, blit=True, 
            repeat_delay=10)
    plt.show()

if __name__ == '__main__':
    lat = create_2d_square_lattice(50)
    lat.run_monte_carlo()
    plot(lat)
