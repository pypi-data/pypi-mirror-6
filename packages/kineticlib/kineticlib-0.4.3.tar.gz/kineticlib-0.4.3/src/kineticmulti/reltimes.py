"""Contains functions for calculating relaxation times
TODO - definition rotrel fix
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

from omegaint import omega
from scipy import constants
from scipy.special import gamma
import crosssection as cs
from molecule_sts import Molecule_sts


def Zr_original(T, eps, infcoll):
    """
    Calculates the collision amount needed to reach rotational equilibrium for HS model, but has an additional
    addendum

    Returns:
    Amount of collisions needed to reach rotational equilibrium

    Takes as input:
    T - the temperature of the mixture
    eps - Lennard-Jones interaction parameter
    infcoll - zeta_{\inf} parameter
    """
    TTstar = eps / T
    F = 1 + 0.5 * (constants.pi ** 1.5) * (TTstar ** 0.5)\
        + (0.25 * (constants.pi ** 2) + 2) * TTstar + (constants.pi ** 1.5) * (TTstar ** 1.5)
    return infcoll / F


def Zr(T, idata, mass, infcoll, model='VSS'):
    """
    Calculates the collision amount needed to reach rotational equilibrium for different models, but has an additional
    addendum

    Returns:
    Amount of collisions needed to reach rotational equilibrium

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    mass - mass of molecule undergoing relaxation
    infcoll - zeta_{\inf} parameter
    model - multiple choice:
        'VSS' - VSS potential
        'VHS' - Variable Hard Sphere potential
        otherwise - Rigid Sphere model
    """
    if model == 'VSS':
        alpha = idata[11] * (T ** idata[12])
        vssomega = idata[6]
    elif model == 'VHS':
        alpha = 1.0
        vssomega = idata[6]
    else:
        alpha = 1.0
        vssomega = 0.0

    TTstar = idata[2] / T
    div = (2.0 - vssomega) / (1.0 + alpha) + 0.5 * (constants.pi ** 1.5) * gamma(1.0 + alpha) * gamma(2.5 - vssomega)\
        * (TTstar ** 0.5) / (gamma(1.5 + alpha) * gamma(2.0 - vssomega)) + (2.0 + 0.25 * (constants.pi ** 2)) * TTstar
    return mass * infcoll / (2.0 * div * idata[0])


def rot_rel_time(T, idata, molecule, n, infcoll, model='IPL'):
    """
    Calculates the rotational relaxation time using Parker's formula and \Omega^{(2,2)} integral

    Returns:
    Rotational relaxation time

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule being considered
    n - the numeric density of the mixture
    infcoll - zeta_{\inf} parameter
    model - model used to calculate the Omega integral:
        'RS' - rigid sphere (then returns result for any l > 0 and r > 0)
        'LJ' - Lennard-Jones (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise returns -1)
        'IPL' - inverse power law (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise returns -1)
        'VSS' - VSS potential (then returns correct result for (l,r) = (1,1) or (l,r) = (2,2), otherwise returns -1)
        'Switch' - returns result for LJ model when T / eps < 10 and for IPL model otherwise; eps is the Lennard-Jones
                   parameter
    """
    return 0.15625 * constants.pi * Zr_original(T, molecule.LJe, infcoll) * constants.pi\
        / (n * omega(T, 2, 2, idata, model=model, nokt=False))  # 0.15625 is 5 / 32


def rot_tel_time_def(T, idata, molecule, partner, n):
    """ Calculates the rotational relaxation time using the definition (through the averaging of the squared
    rotational energy difference)

    Returns:
    Rotational relaxation time

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule which relaxates
    n - the numeric density of the mixture
    """
    if molecule.name == partner.name:
        return 0.5 / (n * cs.elastic_integral(T, 0, idata) * (2 * cs.dE_rot_sq(T, molecule)
                                                              + 2 * cs.dE_rot_c_dE_rot_d(T, molecule, molecule)))
    else:
        if isinstance(partner, Molecule_sts):
            return 0.25 / (n * cs.elastic_integral(T, 0, idata) * cs.dE_rot_dE_rot_full(T, molecule, partner))
        else:
            return 0.25 / (n * cs.elastic_integral(T, 0, idata) * cs.dE_rot_sq(T, molecule))


def rot_rel_time_VSS(T, idata, n, mass, infcoll, model='VSS'):
    """ Calculates the rotational relaxation time using the VSS/VHS/HS models and Parker's formula.

    Returns:
    Rotational relaxation time

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    n - the numeric density of the mixture
    mass - the mass of the relaxating molecule
    infcoll - zeta_{\inf} parameter
    model - multiple choice:
        'VSS' - VSS potential
        'VHS' - Variable Hard Sphere potential
        otherwise - Rigid Sphere model
    """
    return Zr(T, idata, mass, infcoll, model) / ((idata[5] * n
                                                * ((8 * constants.k * T / (constants.pi * idata[0])) ** 0.5)
                                                * (T ** -idata[6]) * gamma(2 - idata[6]))
                                               * (constants.physical_constants['Angstrom star'][0] ** 2))


def millikan_white(T, idata, molecule, p):
    """ Calculates the VT relaxation time using the Millikan-White formula.

    Returns:
    VT relaxation time

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule which undergoes VT relaxation
    p - the pressure (in atmospheres)
    """
    mu = idata[0] * 1000.0 * constants.N_A
    return (10.0 ** (0.0005 * (mu ** 0.5) * ((molecule.hvc / constants.k) ** (4.0 / 3.0))
                     * (T ** (-1.0 / 3.0) - 0.015 * (mu ** 0.25)) - 8.0)) / p
