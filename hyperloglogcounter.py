import numpy as np
from scipy.integrate import quad
import math


class HyperLogLogCounter():
    """ HyperLogLogCounter from https://arxiv.org/pdf/1308.2144v2.pdf
    alpha is calcualted as in http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
    """
    def __init__(self, b, hash_to, debug=False):
        """Init.
        
        Parameters
        ----------
        b : int
            Number of bits in counter registers. Defines the number of registers p=2^b.
        hash_to : int
            Hashing to n bits. E.g.: 32 so hasing items (str or str of int) to 32 bits integers.
        debug : bool
            If True, print debug info.
        """
        # p is the number of registers in the counter, analogous to precision
        self.b = b
        self.p = 2**self.b
        # hash node ids to hash_to number of bits
        self.hash_to = hash_to
        self.format = f'#0{self.hash_to + 2}b'
        # general hash mask to get hash_values with hash_to number of bits
        self.hash_mask = pow(2, self.hash_to) - 1
        # mask for getting the left b number of bits as int
        self.hash_mask_left = 2**self.b - 1
        # mask for getting the hash_to - b (rest from right) number of bits as int
        self.hash_mask_right = self.hash_mask >> self.b
        # counter register (array)
        self.counter = [-np.inf for i in range(self.p)]
        # alpha from http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
        self.alpha = (self.p * quad(lambda u: math.log2((2 + u) / (1 + u)) ** self.p, 0, np.inf)[0])**(-1)
        self.debug = debug
    
    def hash_func(self, x):
        """Hash a node id to an int. E.g.: 32-bit hash of the string value of node ID as int
        
        Parameters
        ----------
        x : int or str
            Node id.
        
        Returns
        -------
        int
            Hashed node id. Hashing to self.hash_to bits (not infinite as in paper).
        """
        xh = hash(str(x)) & self.hash_mask
        if self.debug:
            print(f"x={x} hashed to xh={format(xh, self.format)}")
        return xh
    
    def get_left_right_split(self, xh):
        """Get the split of the binary representation of a node id - left self.b bits and the rest.
        
        Parameters
        ----------
        xh : int
            Hashed node id, binary representation if self.hash_to bits long.
        
        Returns
        -------
        int, int
            left is the left self.b bits as int, and right is the rest of the bits on the right as int 
        """
        # get the left b number of bits as int
        left = xh >> (self.hash_to - self.b) & self.hash_mask_left
        # get the right hash_to-b number of bits as int
        right = xh & self.hash_mask_right
        if self.debug:
            print(f"xh={format(xh, self.format)}, left={format(left, f'#0{self.b+2}b')}, "
                  f"right={format(right, f'#0{self.hash_to-self.b+2}b')}")
        return left, right
    
    def get_leading_zeros_plus_one(self, h):
        """Get the number of leading zeroes +1 in the binary repr of a 
        hashed int (the right hand-side bits usually).
        
        Parameters
        ----------
        h : int
            Hashed value, usually righ-hand side bits, of length self.hash_to - self.b.
        
        Returns
        -------
        l0s: int
            The number of leading zeroes of the binary repr of the right hand-side bit sequence 
            that is self.hash_to - self.b long. 
        """
        l0s = self.hash_to - self.b - h.bit_length() + 1
        if self.debug:
            print(f"h={format(h, self.format)}, l0+1={l0s}")
        return l0s
    
    def size(self, ):
        """Get the size of a counter.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        e: float
            The size of the counter.
        """
        z = sum([2**(-el) for el in self.counter])**(-1)
        e = self.alpha * z * self.p**2
        if self.debug:
            print(f"z={z}, e={e}")
        return e
    
    def add(self, x):
        """Add a node id to the counter.
        
        Parameters
        ----------
        x : int
            A node id.
        
        Returns
        -------
        None
        """
        # hash the node id
        xh = self.hash_func(x)
        # get the left self.b bit sequence and the self.hash_to - self.b sequence from the right (the rest)
        l, r = self.get_left_right_split(xh)
        # save old value
        old = self.counter[l]
        # get the number of leading zeroes + 1 of the right hand side bit sequence.
        l0s = self.get_leading_zeros_plus_one(r)
        # update counter
        self.counter[l] = max(old, l0s)
        if self.debug:
            print(f"before={old}, after={self.counter[l]}")
    
    def __repr__(self, ):
        """Repr."""
        repr_str = f"b={self.b}, p={self.p}, "
