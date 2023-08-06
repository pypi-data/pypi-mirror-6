"""Loads data for omega, generalized omega and dissociation rates calculation
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"


import numpy as np
from csv import reader
from os.path import normcase, join, split
from scipy import constants
from errors import NoDataError


def load_elastic_parameters(partner1, partner2):
    """Loads interaction parameters for two partners for use in various integrals (loads Lenard-Jones, IPL and VSS
    potential parameters + calculates collision radius and collision-reduced mass) from the file interactions.csv
    The values are stored as the following units:
    phizero - electron-volt, beta - 1 / Angstrom

    Returns:
    An array, which contains the following quantities:
    result[0] - collision-reduced mass
    result[1] - collision diameter
    result[2] - Lennard-Jones epsilon parameter
    result[3] - phizero parameter for the IPL potential, divided by the Boltzmann constant (i.e. expressed as a
                                                                                            temperature)
    result[4] - beta parameter for the IPL potential
    result[5] - C parameter for the VSS model for the Omega^(1,1) integral
    result[6] - omega parameter for the VSS model for the Omega^(1,1) integral
    result[7] - C parameter for the VSS model for the Omega^(2,2) integral
    result[8] - omega parameter for the VSS model for the Omega^(2,2) integral
    result[9] - C parameter for the VSS model for the Omega_total integral
    result[10] - omega parameter for the VSS model for the Omega_total integral
    result[11] - C parameter for the VSS model for the deflection angle
    result[12] - omega parameter for the VSS model for the deflection angle

    Takes as input:
    partner1 - the first colliding partner
    partner2 - the second colliding partner

    Notes:
    Deflection angle parameters are needed to calculate amount of collisions needed to establish rotational
    equilibrium using the VSS model
    """
    m = (partner1.mass * partner2.mass)/(partner1.mass + partner2.mass)
    sigma = (partner1.LJs + partner2.LJs) * 0.5
    eps = np.sqrt(partner1.LJe * partner2.LJe * ((partner1.LJs * partner2.LJs) ** 6)) / (sigma ** 6)
    this_dir, this_filename = split(__file__)
    csv_file_object = reader(open(join(this_dir, normcase('data/models/interactions.csv')), 'r'))
    csv_file_object.next()
    res = np.zeros(13)
    res[:3] = [m, sigma, eps]

    for row in csv_file_object:
        if (row[0] == partner1.name and row[1] == partner2.name) or\
                (row[1] == partner1.name and row[0] == partner2.name):
            rd = np.array(row[2:]).astype(np.float64)
            res[3:] = [rd[0], rd[1], rd[2], rd[3], rd[4], rd[5], rd[6], rd[7], rd[8], rd[9]]

    res[3] *= constants.physical_constants['electron volt'][0] / constants.k
    res[4] *= 1.0 / constants.physical_constants['Angstrom star'][0]
    return res


def load_dissociation_parameters(molecule_name, partner_name):
    """Loads dissociation model parameters for the reaction molecule + partner -> atom1 + atom2 + partner. Loads
    parameters for the Arrhenius model, which is considered to be as follows:
    k = A * T^n

    Returns:
    An array, which contains the following quantities:
    result[0] - Arrhenius n parameter
    result[1] - Arrhenius A parameter

    Takes as input:
    molecule_name - a string, the name of the molecule which dissociates
    partner_name - a string, the name of the collision partner
    """
    this_dir, this_filename = split(__file__)
    csv_file_object = reader(open(join(this_dir, normcase('data/models/dissociation.csv')), 'r'))
    csv_file_object.next()
    found = False
    for row in csv_file_object:
        if row[0] == molecule_name and row[1] == partner_name:
            dat = [row[2], row[3]]
            res = np.array(dat).astype(np.float64)
            res[1] *= (10 ** 16) / constants.N_A
            return res
    if found is False:
        raise NoDataError(molecule_name, partner_name, 'dissociation',
                          str(join(this_dir, normcase('data/models/dissociation.csv'))))