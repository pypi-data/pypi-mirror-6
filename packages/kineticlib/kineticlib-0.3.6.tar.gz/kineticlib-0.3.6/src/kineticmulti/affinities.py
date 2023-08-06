"""Contains functions for calculating generalized affinities (and related things) in the multi-temperature
approximation. Serves as a basis for most other modules"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__version__ = "0.3.5"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from scipy.optimize import brentq


def Gamma_VT(vibr_one, T, T1):
    """Calculates Gamma_VT for a one-quantum VT transition: M(i) + P -> M(i-1) + P

    Returns:
    Generalized affinity Gamma_VT

    Takes as input:
    vibr_one - the energy of the first vibrational level of the molecule undergoing the VT transition (molecule
    energy levels are considered to be counted from zero)
    T - the temperature of the mixture
    T1 - the vibrational temperature for the molecule2
    """
    return 1.0 - np.exp((vibr_one * (1.0 / T1 - 1.0 / T)) / constants.k)


def Gamma_diss(molecule, T, T1, n_molecule, n_atom1, n_atom2, diss_level):
    """Calculates Gamma_diss for a dissociation reaction: AB(diss_level) + P -> A + B + P

    Returns:
    Generalized affinity Gamma_diss

    Takes as input:
    molecule - the molecule which dissociates
    T - the temperature of the mixture
    T1 - the vibrational temperature for the molecule
    n_molecule - the numeric density of the molecule
    n_atom1 - the numeric density of the first atomic species which make up the molecule
    n_atom2 - the numeric density of the second atomic species which make up the molecule
    diss_level - the vibrational level at which the molecule is located
    """
    add = molecule.Z_vibr(T, T1) * molecule.Z_rot(T) * (n_atom1 * n_atom2) * (constants.h ** 3)\
                                 * ((2.0 / (molecule.mass * constants.pi * constants.k * T)) ** 1.5) / n_molecule
    add = add * np.exp(molecule.diss / (constants.k * T) + molecule.vibr_one(1) * ((1.0 / T1 - 1.0 / T) / constants.k)
                       * diss_level)
    return 1 - add


def Gamma_diss_binary_equilibrium_xatom(x_atom, molecule, T, n):
    """A helper function, which calculates Gamma_diss (multiplied by the numeric density of the molecules) for a binary
    mixture (A2, A) in vibrational equilibrium (T=T1): A2 + A -> 3A

    Returns:
    Gamma_diss multiplied by the numeric density of the molecules

    Takes as input:
    x_atom - the relative concentration of atoms
    molecule - the molecule which dissociates
    T - the temperature of the mixture
    n - the total numeric density of the mixture
    """
    n_atom = x_atom * n
    mult = molecule.Z_vibr(T, T) * molecule.Z_rot(T) * (n_atom ** 2) * (constants.h ** 3)\
                                 * ((2.0 / (molecule.mass * constants.pi * constants.k * T)) ** 1.5)\
                                 * np.exp(molecule.diss / (constants.k * T))
    return (n - n_atom) - mult


def find_natom_Gamma_diss_binary(molecule, T, n):
    """Finds the numeric density of atoms in a binary mixture (A2, A) in vibrational equilibrium (T=T1) at which
    chemical equilibrium occurs (Gamma_diss = 0)

    Returns:
    n_atom - the numeric density of atoms

    Takes as input:
    molecule - the molecule which dissociates
    T - the temperature of the mixture
    n - the total numeric density of the mixture

    Notes:
    uses the 1973 Brent method. Gamma (when considered as function of xN) changes its' sign on the interval [0, 1],
    is continuous, so it satisfies the conditions needed for the method to work.
    """
    return brentq(Gamma_diss_binary_equilibrium_xatom, 0, 1, xtol=0.0001, maxiter=1000, args=(molecule, T, n))