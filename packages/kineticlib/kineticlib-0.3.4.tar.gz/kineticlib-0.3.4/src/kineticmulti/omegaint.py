"""Contains formulas for elastic omega integrals for various cross-section parameters, plus a function which
loads interaction parameters
TODO - LJ and IPL for various other Omega^(l, r) integrals, VSS too perhaps?
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__version__ = "0.3.1"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"


import numpy as np
from scipy import constants
from csv import reader
from scipy.special import gamma
from os.path import normcase, join, split
from scipy.misc import factorial
from errors import OmegaError


def load_interaction(partner1, partner2):
    """Loads interaction parameters for two partners for use in various integrals (loads Lenard-Jones, IPL and VSS
    potential parameters + calculates collision radius and collision-reduced mass) from the file interactions.csv
    The values are stored as the following units:
    phizero - electron-volt, beta - 1 / Angstrom

    Returns:
    An array, which contains the following quantities:
    result[0] - collision-reduced mass
    result[1] - collision radius
    result[2] - Lennard-Jones epsilon parameter
    result[3] - phizero parameter for the IPL potential, divided by Boltzmann constants (i.e. expressed as a
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
            rd = np.array(row[2:]).astype(np.float)
            res[3:] = [rd[0], rd[1], rd[2], rd[3], rd[4], rd[5], rd[6], rd[7], rd[8], rd[9]]

    res[3] *= constants.physical_constants['electron volt'][0] / constants.k
    res[4] *= 1.0 / constants.physical_constants['Angstrom star'][0]
    return res


def rigid_sphere_omega(T, l, r, m, sigma, nokt=False):
    """Returns the Omega^(l,r)-integral for a rigid sphere potential for any l > 0  and r > 0

    Returns:
    Omega^(l,r) integral for a rigid sphere potential

    Takes as input:
    T - the temperature of the mixture
    l - the degree of the velocity
    r - the degree of the sinus
    m - collision-reduced mass
    sigma - collision radius
    nokt - if False, then returns the usual generalized omega integral; if True, returns the generalized omega
    integral multiplied by (kT) ** (-0.5)
    """
    if nokt is False:
        mult = (T * constants.k / (2.0 * constants.pi * m)) ** 0.5
    else:
        mult = (1.0 / (2.0 * constants.pi * m)) ** 0.5

    return 0.5 * mult * constants.pi * factorial(r + 1) * (1.0 - 0.5 * (1.0 + (-1) ** l) / (l + 1)) * (sigma ** 2)


def omega_dimless_LJ(T, l, r, eps):
    """Returns the dimensionless Omega^(l,r)-integral for a Lennard-Jones (LJ) potential for
    (l,r) = (1,1) or (l,r) = (2,2)

    Returns:
    Dimensionless Omega^(l,r) integral for an LJ potential

    Takes as input:
    T - the temperature of the mixture
    l - the degree of the velocity
    r - the degree of the sinus
    eps - Lennard-Jones interaction parameter
    """
    if l == r:
        if l == 1:
            tmp = np.log(T / eps) + 1.4
            f = [-0.16845, -0.02258, 0.19779, 0.64373, -0.09267, 0.00711]
        elif l == 2:  # l = 2
            tmp = np.log(T / eps) + 1.5
            f = [-0.40811, -0.05086, 0.3401, 0.70375, -0.10699, 0.00763]
        else:
            raise OmegaError('LJ', l, r)
        return 1.0 / (f[0] + f[1] / (tmp ** 2) + f[2] / tmp + f[3] * tmp
                    + f[4] * (tmp ** 2) + f[5] * (tmp ** 3))
    else:
        raise OmegaError('LJ', l, r)


def omega_dimless_IPL(T, l, r, sigma, eps, phizero, beta):
    """Returns the dimensionless Omega^(l,r)-integral for an inverse power law (IPL) potential for
    (l,r) = (1,1) or (l,r) = (2,2)

    Returns:
    Dimensionless Omega^(l,r) integral for an IPL potential

    Takes as input:
    T - the temperature of the mixture
    l - the degree of the velocity
    r - the degree of the sinus
    sigma - collision radius
    phizero - first IPL parameter
    beta - second IPL parameter
    """
    if l == r:
        Tstar = T / eps
        vstar = phizero / eps
        rstar = 1.0 / (beta * sigma)
        Abig = np.zeros(3)
        if l == 1:
            a = np.array([[-267.0, 201.57, 174.672, 54.305],
                          [26700, -19226.5, -27693.8, -10860.9],
                          [-8.9, 6.3201, 10.227, 5.4304]])
            a[2, :] = a[2, :] * 100000
            coeff = 0.89
            pows = np.array([2, 4, 6])
            TT = Tstar
        elif l == 2:  # l == 2
            a = np.array([[-33.0838, 20.0862, 72.1059, 68.5001],
                          [101.571, -56.4472, -286.393, -315.4531],
                          [-87.7036, 46.313, 227.146, 363.1807]])
            coeff = 1.04
            pows = np.array([2, 3, 4])
            TT = np.log(vstar / 10)
        else:
            raise OmegaError('IPL', l, r)
        Abig[:] = a[:, 0] + (a[:, 1] + a[:, 2] / np.log(vstar / 10) + a[:, 3] / ((np.log(vstar / 10)) ** 2)) /\
                  ((rstar * np.log(vstar / 10)) ** 2)
        return (coeff + Abig[0] / (TT ** pows[0]) + Abig[1] / (TT ** pows[1]) + Abig[2] / (TT ** pows[2])) *\
               ((rstar * np.log(vstar / Tstar)) ** 2)
    else:
        raise OmegaError('IPL', l, r)


def omega_vss(T, l, m, vssc, vsso, nokt=False):
    """Returns the Omega^(l,r)-integral for a VSS potential for
    (l,r) = (1,1) or (l,r) = (2,2)

    Returns:
    Omega^(l,r) integral for a VSS potential

    Takes as input:
    T - the temperature of the mixture
    l - the degree of the velocity
    r - the degree of the sinus
    vssc - first VSS parameter radius
    vsso - second VSS parameter
    """
    if nokt is False:
        multiplier = vssc * ((T * constants.k / (2 * constants.pi * m)) ** 0.5) * (T ** (-vsso))
    else:
        multiplier = vssc * ((1 / (2 * constants.pi * m)) ** 0.5) * (T ** (-vsso))
    if l == 1:
        integral = 0.5 * gamma(3 - vsso)
        return multiplier * integral * (constants.physical_constants['Angstrom star'][0] ** 2)
    elif l == 2:
        integral = 0.5 * gamma(4 - vsso)
        return multiplier * integral * (constants.physical_constants['Angstrom star'][0] ** 2)
    else:
        raise OmegaError('VSS', l, l)


def omega(T, l, r, idata, model='IPL', dim=1, nokt=False):
    """Returns the Omega^(l,r)-integral for a specified potential

    Returns:
    Omega^(l,r) integral for specified potential

    Takes as input:
    T - the temperature of the mixture
    l - the degree of the velocity
    r - the degree of the sinus
    idata - collision data for the species involved
    model - multiple choice:
        'RS' - rigid sphere (then returns result for any l > 0 and r > 0)
        'LJ' - Lennard-Jones (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise returns -1)
        'IPL' - inverse power law (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise returns -1)
        'VSS' - VSS potential (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise returns -1)
        'Switch' - returns result for LJ model when T / eps < 10 and for IPL model otherwise; eps is the Lennard-Jones
                   parameter
    dim - if 1, returns dimensional omega-integral, otherwise returns dimensionless (divided by an omega integral
    of the same degree for the rigid-sphere model) omega-integral
    nokt - if False, then returns the usual generalized omega integral; if True, returns the generalized omega
    integral multiplied by (kT) ** (-0.5)
    """
    m = idata[0]
    sigma = idata[1]
    eps = idata[2]
    phizero = idata[3]
    beta = idata[4]
    vssc_11 = idata[5]
    vsso_11 = idata[6]
    vssc_22 = idata[7]
    vsso_22 = idata[8]

    if model == 'LJ':
            if dim == 1:
                return omega_dimless_LJ(T, l, r, eps) * rigid_sphere_omega(T, l, r, m, sigma, nokt)
            else:
                return omega_dimless_LJ(T, l, r, eps)
    elif model == 'RS':
        return rigid_sphere_omega(T, l, r, m, sigma, nokt)
    elif model == 'Switch':  # eps/kT > 10
        if T / eps > 10:
            om_dimless = omega_dimless_IPL(T, l, r, sigma, eps, phizero, beta)
        else:
            om_dimless = omega_dimless_LJ(T, l, r, eps)
        if dim == 1:
            return om_dimless * rigid_sphere_omega(T, l, r, m, sigma)
        else:
            return om_dimless
    elif model == 'IPL':
        if dim == 1:
            return omega_dimless_IPL(T, l, r, sigma, eps, phizero, beta) * rigid_sphere_omega(T, l, r, m, sigma, nokt)
        else:
            return omega_dimless_IPL(T, l, r, sigma, eps, phizero, beta)
    elif model == 'VSS':
        if l == 1 and r == 1:
            if dim == 1:
                return omega_vss(T, l, m, vssc_11, vsso_11, nokt)
            else:
                return omega_vss(T, l, m, vssc_11, vsso_11, nokt) / rigid_sphere_omega(T, l, r, m, sigma, nokt)
        elif l == 2 and r == 2:
            if dim == 1:
                return omega_vss(T, l, m, vssc_22, vsso_22, nokt)
            else:
                return omega_vss(T, l, m, vssc_22, vsso_22, nokt) / rigid_sphere_omega(T, l, r, m, sigma, nokt)
        else:
            raise OmegaError('VSS', l, r)