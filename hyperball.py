from hyperloglogcounter import HyperLogLogCounter
import numpy as np
from tqdm import tqdm
import copy
import sys


class HyperBall():
    """ HyperBall from https://arxiv.org/pdf/1308.2144v2.pdf
    alpha is calcualted as in http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
    """
    def __init__(self, b, hash_to, g):
        """Init.
        
        Parameters
        ----------
        b : int
            Number of bits in counter registers. Defines the number of registers p=2^b.
        hash_to : int
            Hashing to n bits. E.g.: 32 so hasing items (str or str of int) to 32 bits integers.
        g : networkx.DiGraph
            Directed graph with inverted edges.
        """
        # set the number of bits in registers, and the number of registers in the 
        # registers of the HyperLogLogCounters
        self.b = b
        self.p = 2**self.b
        # g is with reversed edges!
        self.g = g
        # fixed node ids in list
        self.nodes = list(g.nodes)
        # init hyperloglogcounters for each node in graph
        self.counters = [HyperLogLogCounter(b=b, hash_to=hash_to) for node in g.nodes]
        # init counters with radius=0
        [self.counters[idx].add(node) for idx, node in enumerate(self.nodes)]
        # if converged
        self.converged = False
        print(f"HyperBall: {self.__repr__()}")

    def union(self, c1, c2):
        """The unnioin of two counters is the counter with the register-wise max of registers.
        
        Parameters
        ----------
        c1 : HyperLogLogCounter
            A HyperLogLogCounter
        c2 : HyperLogLogCounter
            Another HyperLogLogCounter
        
        Returns
        -------
        c_union: HyperLogLogCounter
            The unnioin of two counters is the counter with the register-wise max of registers.
        """
        c_union = copy.deepcopy(c1)
        for i in range(self.p):
            c_union.counter[i] = max(c1.counter[i], c2.counter[i])
        return c_union
    
    def __call__(self,):
        """Fit the HyperBal to estimate the harmonic centrality of each node in the directed graph self.g.reverse()
        
        Parameters
        ----------
        None
        
        Returns
        -------
        dict
            A dict with node ids as keys and their corresponding hamronic centralities as values.
        """
        print(f"Fitting HyperBall ...")
        # start from radius=1, as radius=0 is accounted for when initalizing the HyperLogLogCounters per node
        radius = 1
        
        harmonic_centrality_estimates_per_radius = []
        converged_ratio = 0.0
        
        # while not converged, do
        while not self.converged:
            self.converged = True
            counters_old = copy.deepcopy(self.counters)
            
            # tqdm
            n_edges = len(self.g.edges)
            edges_tqdm = tqdm(enumerate(self.g.edges), total=n_edges, file=sys.stdout,
                              bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
            edges_tqdm.set_description(f"radius={radius}, convergence: {converged_ratio*100:.4f}%, edges: ")
            
            # iterate over edges in teh reversed directed graph, i.e.: stream graph edge by edge
            for idx_edge, (node, neighbour) in edges_tqdm:
                idx_node = self.nodes.index(node)
                idx_neighbour = self.nodes.index(neighbour)
                
                # get counter for node = estimate of the set size of the ball at radius t-1
                a = self.counters[idx_node]
                # update the counter for node = estimate of the set size of the ball at radius t
                a = self.union(c1=a, c2=counters_old[idx_neighbour])
                
                # if ball sizes at radius t and t-1 are not the same, then algorithm is not converged
                if a.size() != self.counters[idx_node].size():
                    converged_ratio += 1
                    self.converged = False
                
                # update the counters = new ball sizes for node
                self.counters[idx_node] = copy.deepcopy(a)
                
            converged_ratio = abs(n_edges - converged_ratio) / n_edges
            
            # compute the harmonic centrailities
            # (self.counters[i].size() - counters_old[i].size()) is the estimate of 
            # the number of nodes at distance t from x), paper p.4, rhs, 2nd equation
            harmonic_centrality_estimates_per_radius.append(
                [(1/radius) * (self.counters[i].size() - counters_old[i].size()) for i, node in enumerate(self.nodes)])
            
            # increase radius
            radius += 1
        
        print(f"HyperBall converged")
        # reduce sum on axis=0 (per node), i.e.: marginalize over radii
        harmonic_centrality_estimates = np.array(harmonic_centrality_estimates_per_radius).sum(axis=0)
        
        # return dict: keys node ids, values harmonic centralities
        return {node: harmonic_centrality_estimates[idx] for idx, node in enumerate(self.nodes)}
                
    def __repr__(self):
        """Repr."""
        repr_str = f"b={self.b}, p={self.p}, len(g.nodes)={len(self.g.nodes)}, len(g.edges)={len(self.g.edges)}"
        return repr_str
