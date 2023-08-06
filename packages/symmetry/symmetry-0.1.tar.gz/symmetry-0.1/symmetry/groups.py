#!/usr/bin/env python

"""
Defines SymmetryGroup parent class and PointGroup and SpaceGroup classes.
Shyue Ping Ong thanks Marc De Graef for his generous sharing of his
SpaceGroup data as published in his textbook "Structure of Materials".
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2013, The Materials Virtual Lab"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "ongsp@ucsd.edu"
__date__ = "4/4/14"

import os
from itertools import product
from fractions import Fraction

import numpy as np

import json


with open(os.path.join(os.path.dirname(__file__), "symm_data.json")) as f:
    SYMM_DATA = json.load(f)

GENERATOR_MATRICES = SYMM_DATA["generator_matrices"]
POINT_GROUP_ENC = SYMM_DATA["point_group_encoding"]
SPACE_GROUP_ENC = SYMM_DATA["space_group_encoding"]
TRANSLATIONS = {k: Fraction(v) for k, v in SYMM_DATA["translations"].items()}


class SymmetryGroup(object):

    def get_orbit(self, p):
        """
        Returns the orbit for a point.

        Args:
            p: Point as a 3x1 array.

        Returns:
            ([array]) Orbit for point.
        """
        orbit = []
        for o in self.symmetry_ops:
            pp = np.dot(o, p)
            pp = np.mod(pp, 1)
            if not in_array_list(orbit, pp):
                orbit.append(pp)
        return orbit


class PointGroup(SymmetryGroup):
    """
    Class representing a Point Group, with generators and symmetry operations.

    .. attribute:: symbol

        Full International or Hermann-Mauguin Symbol.

    .. attribute:: generators

        List of generator matrices. Note that 3x3 matrices are used for Point
        Groups.

    .. attribute:: symmetry_ops

        Full set of symmetry operations as matrices.
    """

    def __init__(self, int_symbol):
        """
        Initializes a Point Group from its international symbol.

        Args:
            int_symbol (str): International or Hermann-Mauguin Symbol.
        """
        self.symbol = int_symbol
        self.generators = [GENERATOR_MATRICES[c]
                           for c in POINT_GROUP_ENC[int_symbol]]
        self.symmetry_ops = self._generate_full_symmetry_ops()

    def _generate_full_symmetry_ops(self):
        symm_ops = list(self.generators)
        new_ops = self.generators
        while len(new_ops) > 0:
            gen_ops = []
            for g1, g2 in product(new_ops, symm_ops):
                op = np.dot(g1, g2)
                if not in_array_list(symm_ops, op):
                    gen_ops.append(op)
                    symm_ops.append(op)
            new_ops = gen_ops
        return symm_ops


class SpaceGroup(SymmetryGroup):
    """
    Class representing a SpaceGroup.

    .. attribute:: symbol

        Full International or Hermann-Mauguin Symbol.

    .. attribute:: int_number

        International number

    .. attribute:: generators

        List of generator matrices. Note that 4x4 matrices are used for Space
        Groups.
    """

    def __init__(self, int_symbol):
        """
        Initializes a Point Group from its *full* international symbol.

        Args:
            int_symbol (str): Full International or Hermann-Mauguin Symbol.
            The notation is a LaTeX-like string, with screw axes being
            represented by an underscore. For example, "P6_3/mmc".
        """
        self.symbol = int_symbol
        # TODO: Support different origin choices.
        enc = list(SPACE_GROUP_ENC[int_symbol]["enc"])
        inversion = int(enc.pop(0))
        ngen = int(enc.pop(0))
        symm_ops = [np.eye(4)]
        if inversion:
            symm_ops.append(np.array(
                [[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0],
                 [0, 0, 0, 1]]))
        for i in xrange(ngen):
            m = np.eye(4)
            m[:3, :3] = GENERATOR_MATRICES[enc.pop(0)]
            m[0, 3] = TRANSLATIONS[enc.pop(0)]
            m[1, 3] = TRANSLATIONS[enc.pop(0)]
            m[2, 3] = TRANSLATIONS[enc.pop(0)]
            symm_ops.append(m)
        self.generators = symm_ops
        self.int_number = SPACE_GROUP_ENC[int_symbol]["int_number"]
        self._symmetry_ops = None

    def _generate_full_symmetry_ops(self):
        symm_ops = np.array(self.generators)
        for op in symm_ops:
            op[0:3, 3] = np.mod(op[0:3, 3], 1)
        new_ops = symm_ops
        while len(new_ops) > 0 and len(symm_ops) < 192:
            gen_ops = []
            for g in new_ops:
                new_ops = np.einsum('ij...,...i', g, symm_ops)
                for op in new_ops:
                    op[0:3, 3] = np.mod(op[0:3, 3], 1)
                    ind = np.where(np.abs(1 - op[0:3, 3]) < 1e-5)
                    op[ind, 3] = 0
                    if not in_array_list(symm_ops, op):
                        gen_ops.append(op)
                        symm_ops = np.append(symm_ops, [op], axis=0)
            new_ops = gen_ops
        return symm_ops

    @property
    def symmetry_ops(self):
        """
        Full set of symmetry operations as matrices. Lazily initialized as
        generation sometimes takes a bit of time.
        """
        if self._symmetry_ops is None:
            self._symmetry_ops = self._generate_full_symmetry_ops()
        return self._symmetry_ops

    def get_orbit(self, p):
        """
        Returns the orbit for a point.

        Args:
            p: Point as a 3x1 array.

        Returns:
            ([array]) Orbit for point.
        """
        p = np.append(p, [1])
        orbit = super(SpaceGroup, self).get_orbit(p)
        return np.delete(orbit, np.s_[-1:], 1)

    @classmethod
    def from_int_number(cls, int_number, hexagonal=True):
        """
        Obtains a SpaceGroup from its international number.

        Args:
            int_number (int): International number.
            hexagonal (bool): For rhombohedral groups, whether to return the
                hexagonal setting (default) or rhombohedral setting.

        Returns:
            (SpaceGroup)
        """
        return SpaceGroup(sg_symbol_from_int_number(int_number,
                                                    hexagonal=hexagonal))

    def __str__(self):
        return "Spacegroup %s with international number %d and order %d" % (
            self.symbol, self.int_number, len(self.symmetry_ops))


def sg_symbol_from_int_number(int_number, hexagonal=True):
    """
    Obtains a SpaceGroup name from its international number.

    Args:
        int_number (int): International number.
        hexagonal (bool): For rhombohedral groups, whether to return the
            hexagonal setting (default) or rhombohedral setting.

    Returns:
        (str) Spacegroup symbol
    """
    syms = []
    for n, v in SPACE_GROUP_ENC.items():
        if v["int_number"] == int_number:
            syms.append(n)
    if len(syms) == 0:
        raise ValueError("Invalid international number!")
    if len(syms) == 2:
        if hexagonal:
            syms = filter(lambda s: s.endswith("H"), syms)
        else:
            syms = filter(lambda s: not s.endswith("H"), syms)
    return syms.pop()


def in_array_list(array_list, a):
    """
    Extremely efficient nd-array comparison using numpy's broadcasting. This
    function checks if a particular array a, is present in a list of arrays.
    It works for arrays of any size, e.g., even matrix searches.
    """
    if len(array_list) == 0:
        return False
    axes = tuple(range(1, a.ndim + 1))
    return np.any(np.sum(np.abs(array_list - a[None, :]), axes) < 1e-5)


if __name__ == "__main__":
    for k in POINT_GROUP_ENC.keys():
        pg = PointGroup(k)
        print "Order of point group %s is %d" % (k, len(pg.symmetry_ops))
    #
    # from sympy import symbols
    # x, y, z = symbols("x y z")
    # p = [x,y,z]
    # pg = PointGroup("m-3m")
    # for r in pg.get_orbit(p):
    #     print r
    # sg = SpaceGroup.from_int_number(1)
    # print sg
    for i in range(1, 231):
        sg = SpaceGroup.from_int_number(i, False)
        print sg


    # print sg.symmetry_ops
    #print len(sg.symmetry_ops)
    #sg = SpaceGroup("Im-3m")
    #print len(sg.symmetry_ops)
    #profile_sg()


