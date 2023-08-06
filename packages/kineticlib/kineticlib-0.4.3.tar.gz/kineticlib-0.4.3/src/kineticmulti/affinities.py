"""Contains functions for calculating generalized affinities (and related things) in the multi-temperature
approximation. Serves as a basis for most other modules"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from scipy.optimize import brentq


def Gamma_VT(molecule, T, T1, delta=-1):
    """Calculates Gamma_VT for a VT transition: M(i) + P -> M(i+delta) + P

    Returns:
    Generalized affinity Gamma_VT

    Takes as input:
    molecule - the molecule undergoing the transition
    T - the temperature of the mixture
    T1 - the vibrational temperature for the molecule
    delta - change in vibrational level
    """
    return 1.0 - np.exp((molecule.vibr_one(1) * delta * (1.0 / T - 1.0 / T1)) / constants.k)


def Gamma_VV(molecule1, molecule2, T, T1_1, T1_2, i_delta, k_delta):
    """Calculates Gamma_VV for a VV transition: M1(i) + M2(k) -> M1(i+i_delta) + M2(k+k_delta)

    Returns:
    Generalized affinity Gamma_VV

    Takes as input:
    molecule1 - molecule M1
    molecule2 - molecule M2
    T1_1 - the vibrational temperature of the molecule M1
    T1_2 - the vibrational temperature of the molecule M2
    delta_i - change in vibrational level of molecule M1
    delta_k - change in vibrational level of molecule M2
    """
    add = i_delta * molecule1.vibr_one(1) * (1.0 - T / T1_1) + k_delta * molecule2.vibr_one(1) * (1.0 - T / T1_2)
    return 1.0 - np.exp(add / (constants.k * T))


def Gamma_22(molecule1, molecule2, molecule_new1, molecule_new2, T, T1_1, T1_2, T1_new1, T1_new2, n_molecule1,
             n_molecule2, n_molecule_new1, n_molecule_new2, i, k, i_new, k_new):
    """Calculates Gamma_22 for a reaction M1(i) + M2(k) -> M3(i_new) + M4(k_new)

    Returns:
    Generalized affinity Gamma_22

    Takes as input:
    molecule1 - molecule M1
    molecule2 - molecule M2
    molecule_new1 - molecule M3, product of the reaction
    molecule_new2 - molecule M4, product of the reaction
    T - the temperature of the mixture
    T1_1 - the vibrational temperature of the molecule M1
    T1_2 - the vibrational temperature of the molecule M2
    T1_new1 - the vibrational temperature of the molecule M3
    T1_new2 - the vibrational temperature of the molecule M4
    n_molecule1 - the numeric density of molecule M1
    n_molecule2 - the numeric density of molecule M2
    n_molecule_new1 - the numeric density of molecule M3
    n_molecule_new2 - the numeric density of molecule M4
    i - vibrational level of molecule M1
    k - vibrational level of molecule M2
    i_new - vibrational level of molecule M3
    k_new - vibrational level of molecule M4
    """
    kT = constants.k * T
    add = molecule1.Z_vibr(T, T1_1) * molecule1.Z_rot(T) * molecule2.Z_vibr(T, T1_2) * molecule2.Z_rot(T)
    add /= molecule_new1.Z_vibr(T, T1_new1) * molecule_new1.Z_rot(T)\
           * molecule_new2.Z_vibr(T, T1_new2) * molecule_new2.Z_rot(T)
    add *= (n_molecule1 * n_molecule2) / (n_molecule_new1 * n_molecule_new2)
    add *= (molecule1.mass * molecule2.mass / (molecule_new1.mass * molecule_new2.mass)) ** 1.5
    add *= np.exp(molecule_new1.form / kT + molecule_new2.form / kT - molecule1.form / kT - molecule2.form / kT)
    add *= np.exp(molecule1.vibr_one(1) * i * (1.0 / (constants.k * T1_1) - 1.0 / kT)
                  + molecule2.vibr_one(1) * k * (1.0 / (constants.k * T1_2) - 1.0 / kT)
                  - molecule_new1.vibr_one(1) * i_new * (1.0 / (constants.k * T1_new1) - 1.0 / kT)
                  - molecule_new2.vibr_one(1) * k_new * (1.0 / (constants.k * T1_new2) - 1.0 / kT))
    return 1.0 - add


def Gamma_diss(molecule, atom1, atom2, T, T1, n_molecule, n_atom1, n_atom2, diss_level):
    """Calculates Gamma_diss for a dissociation reaction: AB(diss_level) + P -> A + B + P

    Returns:
    Generalized affinity Gamma_diss

    Takes as input:
    molecule - the molecule which dissociates
    atom1 - atom of the first atomic species which make up the molecule
    atom2 - atom of the second atomic species which make up the molecule
    T - the temperature of the mixture
    T1 - the vibrational temperature for the molecule
    n_molecule - the numeric density of the molecule
    n_atom1 - the numeric density of the first atomic species which make up the molecule
    n_atom2 - the numeric density of the second atomic species which make up the molecule
    diss_level - the vibrational level at which the molecule is located
    """
    add = molecule.Z_vibr(T, T1) * molecule.Z_rot(T) * (n_atom1 * n_atom2) * (constants.h ** 3)\
                                 * ((molecule.mass / (2.0 * atom1.mass * atom2.mass * constants.pi
                                                      * constants.k * T)) ** 1.5) / n_molecule
    add = add * np.exp(molecule.diss / (constants.k * T) + molecule.vibr_one(1) * ((1.0 / T1 - 1.0 / T) / constants.k)
                       * diss_level)
    return 1.0 - add


def Gamma_diss_binary_equilibrium_xatom(x_atom, molecule, atom1, atom2, T, n):
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
                                 * ((molecule.mass / (2.0 * atom1.mass * atom2.mass * constants.pi
                                                      * constants.k * T)) ** 1.5)\
                                 * np.exp(molecule.diss / (constants.k * T))
    return (n - n_atom) - mult


def find_natom_diss_eq(molecule, atom1, atom2, T, n):
    """Finds the numeric density of atoms in a binary mixture (A2, A) in vibrational equilibrium (T=T1) at which
    chemical equilibrium occurs (Gamma_diss = 0)

    Returns:
    n_atom - the numeric density of atoms

    Takes as input:
    molecule - the molecule which dissociates
    atom1 - atom of the first atomic species which make up the molecule
    atom2 - atom of the second atomic species which make up the molecule
    T - the temperature of the mixture
    n - the total numeric density of the mixture

    Notes:
    uses the 1973 Brent method. Gamma (when considered as function of xN) changes its' sign on the interval [0, 1],
    is continuous, so it satisfies the conditions needed for the method to work.
    """
    return brentq(Gamma_diss_binary_equilibrium_xatom, 0, 1, xtol=0.0001, maxiter=1000, args=(molecule, atom1, atom2,
                                                                                              T, n))