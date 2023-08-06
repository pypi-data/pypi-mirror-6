"""Contains formulas for elastic omega integrals for various cross-section parameters, plus a function which
loads interaction parameters
TODO - LJ and IPL for various other Omega^(l, r) integrals, VSS too perhaps?
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"


import numpy as np
from scipy import constants
from scipy.special import gamma
from scipy.misc import factorial
from errors import OmegaError


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
        'LJ' - Lennard-Jones (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise raises error
        'IPL' - inverse power law (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise raises error
        'VSS' - VSS potential (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise raises error
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