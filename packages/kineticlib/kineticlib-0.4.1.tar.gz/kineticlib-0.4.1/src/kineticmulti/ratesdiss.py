"""Contains functions for calculating dissociation rates
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__version__ = "0.3.5"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from crosssection import diss_integral_rigid_sphere


def k_diss_eq(T, model_data, diss_energy):
    """Calculates the equilibrium rate constant using the Arrhenius model

    Returns:
    Equilibrium rate constant

    Takes as input:
    T - the temperature of the mixtrue
    model_data - dissociation model data
    diss_energy - dissociation energy
    """
    return model_data[1] * (T ** model_data[0]) * np.exp(-diss_energy/(constants.k * T))


def diss_rate_treanor_marrone(T, model_data, molecule, i, model='D6k'):
    """Calculates the non-equilibrium rate constant using the Treanor-Marrone model

    Returns:
    Non-equilibrium dissociation rate constant

    Takes as input:
    T - the temperature of the mixtrue
    molecule - the molecule which dissociates
    i - the vibrational level from which it dissociates
    model_data - dissociation model data
    model - multiple options:
            if equal to 'inf', the U parameter in the non-equilbrium factor will be equal to infinity
            if equal to 'D6k', the U parameter in the non-equilbrium factor will be equal to D / 6k,
                               where D is the dissociation energy of the molecule
            if equal to '3T', the U parameter in the non-equilbrium factor will be equal to 3T
    """
    return molecule.Z_diss(i, T, model) * k_diss_eq(T, model_data, molecule.diss)


def diss_rate_rigid_sphere(T, idata, molecule, i, center_of_mass=True):
    """Calculates the non-equilibrium rate constant using the rigid-sphere crosssection

    Returns:
    Non-equilibrium dissociation rate constant

    Takes as input:
    T - the temperature of the mixtrue
    idata - collision data for the species involved
    molecule - the molecule which dissociates
    i - the vibrational level from which it dissociates
    center_of_mass - specifies the model being used (if False, the simpler rigid sphere model will be used, otherwise,
    the rigid sphere model depending on the relative energy along the center-of-mass line will be used)
    """
    return 8.0 * diss_integral_rigid_sphere(T, 0, idata, molecule, i, center_of_mass)