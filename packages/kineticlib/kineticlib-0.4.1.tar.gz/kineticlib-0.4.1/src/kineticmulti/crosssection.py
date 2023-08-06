"""Contains elastic and various inelastic crosssections and generalized omega integrals
TODO - VT singleup, singledown
TODO2 - dissociation crosssection based on VSS?
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__version__ = "0.3.5"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"

import numpy as np
from scipy import constants
from scipy.special import gamma
from scipy.misc import factorial
from scipy import integrate
import probabilities as prob
from errors import ProbError


def diss_integral_rigid_sphere(T, deg, idata, molecule, i, center_of_mass=True, nokt=False):
    """Calculates the generalized dissociation omega integral either using the rigid sphere model or the rigid sphere
    model depending on the relative energy along the center-of-mass line

    Returns:
    Generalized dissociation omega integral

    Takes as input:
    T - the temperature of the mixture
    deg - the degree
    idata - collision data for the species involved
    molecule - the molecule which dissociates
    i - the vibrational level from which it dissociates
    center_of_mass - specifies the model being used (if False, the simpler rigid sphere model will be used, otherwise,
    the rigid sphere model depending on the relative energy along the center-of-mass line will be used)
    nokt - if False, then returns the usual generalized omega integral; if True, returns the generalized omega
    integral multiplied by (kT) ** (-0.5)

    Notes:
    if degree is not 0, it is considered to be 1
    """
    if nokt is False:
        multiplier = constants.pi * (idata[1] ** 2) * ((constants.k * T / (2 * constants.pi * idata[0])) ** 0.5)
    else:
        multiplier = constants.pi * (idata[1] ** 2) * ((0.5 / (constants.pi * idata[0])) ** 0.5)
    min_sq = (molecule.diss - molecule.vibr[i]) / (constants.k * T)
    if deg == 0:
        if center_of_mass is False:
            return 0.5 * multiplier * np.exp(-min_sq)
        else:
            return multiplier * 0.5 * (min_sq + 1.0) * np.exp(-min_sq)
    else:
        if center_of_mass is False:
            return 0.5 * multiplier * (min_sq + 2.0) * np.exp(-min_sq)
        else:
            return multiplier * 0.5 * ((min_sq ** 2) + 2.0 * min_sq + 1.0) * np.exp(-min_sq)  # re-check!


def elastic_integral(T, deg, idata, rig_sphere=False, nokt=False):
    """Calculates the generalized elastic omega integral either using the rigid sphere model or VSS model

    Returns:
    Generalized elastic omega integral

    Takes as input:
    T - the temperature of the mixture
    deg - the degree
    idata - collision data for the species involved
    rig_sphere - specifies the model being used (if True, the simpler rigid sphere model will be used)
    nokt - if False, then returns the usual generalized omega integral; if True, returns the generalized omega
    integral multiplied by (kT) ** (-0.5)
    """
    if rig_sphere is False:
        if nokt is False:
            multiplier = idata[9] * ((T * constants.k / (2.0 * constants.pi * idata[0])) ** 0.5) * (T ** (-idata[10]))
        else:
            multiplier = idata[9] * ((0.5 / (constants.pi * idata[0])) ** 0.5) * (T ** (-idata[10]))
        return 0.5 * gamma(2.0 - idata[10] + deg) * (constants.physical_constants['Angstrom star'][0] ** 2) * multiplier
    else:
        if nokt is False:
            multiplier = ((T * constants.k / (2.0 * constants.pi * idata[0])) ** 0.5)
        else:
            multiplier = ((0.5 / (constants.pi * idata[0])) ** 0.5)
        if deg == 0:
            return multiplier * 0.25 * constants.pi * (idata[1] ** 2)
        else:
            return 0.0


def elastic_crosssection(g, deg, vsso):
    """Helper function, calculates the velocity-dependent generalized elastic integral cross-section using the VSS model
    multiplied by exp(-g^2)

    Returns:
    Generalized elastic integral cross-section

    Takes as input:
    g - the dimensionless velocity
    deg - the degree
    vsso - the omega parameter in the VSS model
    """
    return np.exp(-(g ** 2)) * (g ** (3 + 2 * (deg - vsso)))


def vt_integral(T, deg, idata, molecule, i, delta, nokt=False):
    """Calculates the generalized VT omega integral using the FHO probability and VSS cross-section models for
    the following process: M(i) + P -> M(i + delta) + P

    Returns:
    Generalized VT omega integral

    Takes as input:
    T - the temperature of the mixture
    deg - the degree
    idata - collision data for the species involved
    molecule - the molecule undergoing the VT transition
    i - the vibrational level of the molecule
    delta - by what value the vibrational level is changed
    nokt - if False, then returns the usual generalized omega integral; if True, returns the generalized omega
    integral multiplied by (kT) ** (-0.5)
    """
    if delta != 0:
        f = lambda g: prob.vt_prob_g_only(g, T, idata, molecule.vibr, i, delta, molecule.vibr_zero + molecule.diss) \
                      * elastic_crosssection(g, deg, idata[10])
        if delta == 1:
            mult = (i + 1)
        elif delta == -1:
            mult = i
        elif delta > 0:
            mult = prob.fact_div_fact(i, i + delta) / (factorial(delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + delta, i) / (factorial(-delta) ** 2)
        if nokt is False:
            return mult * (constants.physical_constants['Angstrom star'][0] ** 2) * idata[9]\
                        * ((T * constants.k / (2.0 * constants.pi * idata[0])) ** 0.5) * (T ** (-idata[10]))\
                        * integrate.quad(f, 0, np.inf)[0]
        else:
            return mult * (constants.physical_constants['Angstrom star'][0] ** 2) * idata[9]\
                        * ((0.5 / (constants.pi * idata[0])) ** 0.5) * (T ** (-idata[10]))\
                        * integrate.quad(f, 0, np.inf)[0]
    else:
        raise ProbError('VT transition', 0, 'i')


def vv_integral(T, deg, idata, molecule1, molecule2, i, k, i_delta, nokt=False):
    """Calculates the generalized VV omega integral using the FHO probability and VSS cross-section models for
    the following process: M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)

    Returns:
    Generalized VV omega integral

    Takes as input:
    T - the temperature of the mixture
    deg - the degree
    idata - collision data for the species involved
    molecule1 - the first molecule undergoing the VV transition
    molecule2 - the second molecule undergoing the VV transition
    i - the vibrational level of the first molecule
    k - the vibrational level of the second molecule
    i_delta - by what value the vibrational level of the first molecule is changed
    nokt - if False, then returns the usual generalized omega integral; if True, returns the generalized omega
    integral multiplied by (kT) ** (-0.5)
    """
    if i_delta != 0:
        f = lambda g: prob.vv_prob_g_only(g, T, idata, molecule1.vibr, molecule2.vibr, i, k, i_delta) \
                      * elastic_crosssection(g, deg, idata[10])
        if i_delta == 1:
            mult = (i + 1) * k
        elif i_delta == -1:
            mult = i * (k + 1)
        elif i_delta > 0:
            mult = prob.fact_div_fact(i, i + i_delta) * prob.fact_div_fact(k - i_delta, k) / (factorial(i_delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + i_delta, i) * prob.fact_div_fact(k, k - i_delta) / (factorial(-i_delta) ** 2)
        if nokt is False:
            return mult * (constants.physical_constants['Angstrom star'][0] ** 2) * idata[9]\
                        * ((T * constants.k / (2.0 * constants.pi * idata[0])) ** 0.5) * (T ** (-idata[10]))\
                        * integrate.quad(f, 0, np.inf)[0]
        else:
            return mult * (constants.physical_constants['Angstrom star'][0] ** 2) * idata[9]\
                        * ((0.5 / (constants.pi * idata[0])) ** 0.5) * (T ** (-idata[10]))\
                        * integrate.quad(f, 0, np.inf)[0]
    else:
        raise ProbError('VV transition', 0, 'i')


def vv_collisions(T, T1_1, T1_2, idata, molecule1, molecule2, nokt=False):
    """Calculates averaging over the VV cross-sections of various vibrational-level/energy-related quantities
    (Basically, calculates <F(i, k)>_{cd}, where <>_{cd} denotes averaging over all VV cross-sections)
    Considers all transitions to be one-quantum

    Returns:
    (To simplifiy notation:
    dE_c is the dimensionless difference between vibrational energies for molecule1
    dE_d is the dimensionless difference between vibrational energies for molecule2
    di is the difference between vibrational levels for molecule1
    dk is the difference between vibrational levels for molecul2)
    An array, which contains the following quantities:
    result[0] - <dE_c ^ 2>_{cd}
    result[1] - <dE_d ^ 2>_{cd}
    result[2] - <dE_c * dE_d>_{cd}
    result[3] - <di * dE_c>_{cd}
    result[4] - <di * dE_d>_{cd}
    result[5] - <dk * dE_c>_{cd}
    result[6] - <dk * dE_d>_{cd}
    result[7] - <dE_c>_{cd}
    result[8] - <dE_d>_{cd}
    result[9] - <di ^ 2>_{cd}
    result[10] - <di * dk>_{cd}
    result[11] - <di>_{cd} (should be negligibly small, since, from a theoretical POV, it is precisely equal to 0)

    Takes as input:

    T - the temperature of the mixture
    T1_1 - the vibrational temperature for molecule1
    T1_2 - the vibrational temperature for molecule2
    idata - collision data for the species involved
    molecule1 - the first molecule undergoing the VV transition
    molecule2 - the second molecule undergoing the VV transition
    i - the vibrational level of the first molecule
    k - the vibrational level of the second molecule
    nokt - if True, the result is multiplied by (kT) ** (-0.5)
    """
    result = np.zeros(12)
    Z = molecule1.Z_vibr(T, T1_1) * molecule2.Z_vibr(T, T1_2)

    a = np.arange(0, molecule1.num_vibr + 1)
    b = np.arange(0, molecule2.num_vibr + 1)

    vibr_energy = molecule1.vibr_energy(a, 0)
    vibr_energy2 = molecule2.vibr_energy(b, 0)
    vibr_exp = molecule1.vibr_exp(a, T, T1_1)
    vibr_exp2 = molecule2.vibr_exp(b, T, T1_2)

    for k in xrange(molecule2.num_vibr):
        for i in xrange(molecule1.num_vibr):
            cs = vv_integral(T, 0, idata, molecule1, molecule2, i, k + 1, 1, nokt)
            result[0] += ((vibr_energy[i] - vibr_energy[i + 1]) ** 2) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[1] += ((vibr_energy2[k + 1] - vibr_energy2[k]) ** 2) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[2] += ((vibr_energy[i + 1] - vibr_energy[i]) * (vibr_energy2[k] - vibr_energy2[k + 1]))\
                * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[3] += (vibr_energy[i + 1] - vibr_energy[i]) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[4] += (vibr_energy2[k] - vibr_energy2[k + 1]) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[5] -= (vibr_energy[i + 1] - vibr_energy[i]) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[6] -= (vibr_energy2[k] - vibr_energy2[k + 1]) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[7] += (vibr_energy[i + 1] - vibr_energy[k + 1]) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[8] += (vibr_energy2[k] - vibr_energy2[k + 1]) * vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[9] += vibr_exp[i] * vibr_exp2[k + 1] * cs  # i, k -> i + 1, k - 1
            result[10] -= vibr_exp[i] * vibr_exp2[k + 1] * cs
            result[11] += vibr_exp[i] * vibr_exp2[k + 1] * cs

            cs = vv_integral(T, 0, idata, molecule1, molecule2, i + 1, k, -1, nokt)
            result[0] += ((vibr_energy[i] - vibr_energy[i + 1]) ** 2)\
                * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <Ev_i^2>
            result[1] += ((vibr_energy2[k] - vibr_energy2[k + 1]) ** 2)\
                * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <Ev_k^2>
            result[2] += ((vibr_energy[i] - vibr_energy[i + 1]) * (vibr_energy2[k + 1] - vibr_energy2[k]))\
                * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <Ev_i Ev_k>
            result[3] -= (vibr_energy[i] - vibr_energy[i + 1]) * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <i * Ev_i>
            result[4] -= (vibr_energy2[k + 1] - vibr_energy2[k]) * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <i Ev_k>
            result[5] += (vibr_energy[i] - vibr_energy[i + 1]) * vibr_exp[i + 1] * vibr_exp2[k] * cs
            result[6] += (vibr_energy2[k + 1] - vibr_energy2[k]) * vibr_exp[i + 1] * vibr_exp2[k] * cs
            result[7] += (vibr_energy[i] - vibr_energy[i + 1]) * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <Ev_i>
            result[8] += (vibr_energy2[k + 1] - vibr_energy2[k]) * vibr_exp[i + 1] * vibr_exp2[k] * cs  # <Ev_k>
            result[9] += vibr_exp[i + 1] * vibr_exp2[k] * cs  # <i ^ 2>
            result[10] -= vibr_exp[i + 1] * vibr_exp2[k] * cs  # <i k>
            result[11] -= vibr_exp[i + 1] * vibr_exp2[k] * cs  # <i>

    return result / Z


def dE_rot_sq(T, molecule):
    """Calculates dE_rot^2, where dE_rot is the dimenionless difference between rotational energies
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot^2, where dE_rot is the dimenionless difference between rotational energies

    Takes as input:
    T - the temperature of the mixture
    molecule - the molecule
    """
    f = lambda j: (2 * molecule.rot_energy(j, 1) * molecule.rot_energy(j + 1, 1)
                   + molecule.rot_energy(j, 1) ** 2
                   + molecule.rot_energy(j + 1, 1) ** 2) * molecule.rot_exp(j, T)
    tmp = integrate.quad(f, 0, molecule.num_rot - 1)[0]
    f = lambda j: (2 * molecule.rot_energy(j, 1) * molecule.rot_energy(j - 1, 1)
                   + molecule.rot_energy(j, 1) ** 2
                   + molecule.rot_energy(j - 1, 1) ** 2) * molecule.rot_exp(j, T)
    tmp += integrate.quad(f, 1, molecule.num_rot)[0]
    tmp *= 0.5 / (molecule.Z_rot(T) * ((constants.k * T) ** 2)) / molecule.num_rot
    return tmp


def dE_rot_single(T, molecule):
    """Calculates dE_rot, where dE_rot is the dimenionless difference between rotational energies
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot, where dE_rot is the dimenionless difference between rotational energies

    Takes as input:
    T - the temperature of the mixture
    molecule - the molecule
    """
    f = lambda j: (molecule.rot_energy(j, 1) - molecule.rot_energy(j + 1, 1)) * molecule.rot_exp(j, T)
    tmp = integrate.quad(f, 0, molecule.num_rot - 1)[0]
    f = lambda j: (molecule.rot_energy(j, 1) - molecule.rot_energy(j - 1, 1)) * molecule.rot_exp(j, T)
    tmp += integrate.quad(f, 1, molecule.num_rot)[0]
    tmp *= 0.5 / (molecule.Z_rot(T) * ((constants.k * T))) / molecule.num_rot
    return tmp


def dE_rot_c_dE_rot_d(T, molecule1, molecule2):
    """Calculates dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference between rotational
    energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies for molecule2
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot_c * dE_rot_d, where dE_rot_c is the dimenionless difference between rotational
    energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies for molecule2

    Takes as input:
    T - the temperature of the mixture
    molecule1 - the first molecule
    molecule2 - the second molecule2
    """
    return dE_rot_single(T, molecule1) * dE_rot_single(T, molecule2)


def dE_rot_dE_rot_full(T, molecule1, molecule2):
    """Calculates dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference between rotational
    energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies for molecule2
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference between rotational
    energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies for molecule2

    Takes as input:
    T - the temperature of the mixture
    molecule1 - the first molecule
    molecule2 - the second molecule2
    """
    return dE_rot_sq(T, molecule1) + dE_rot_single(T, molecule1) * dE_rot_single(T, molecule2)


def dE_rot_sq_integral(T, idata, molecule, nokt=False):
    """Calculates the full averaging of dE_rot^2, where dE_rot is the dimenionless difference between rotational energies
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot^2, where dE_rot is the dimenionless difference between rotational energies

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule
    nokt - if True, the result is multiplied by (kT) ** (-0.5)
    """
    return dE_rot_sq(T, molecule) * elastic_integral(T, 0, idata, nokt=nokt)


def dE_rot_single_integral(T, idata, molecule, nokt=False):
    """Calculates the full averaging of dE_rot, where dE_rot is the dimenionless difference between rotational energies
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot, where dE_rot is the dimenionless difference between rotational energies

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule
    nokt - if True, the result is multiplied by (kT) ** (-0.5)
    """
    return dE_rot_single(T, molecule) * elastic_integral(T, 0, idata, nokt=nokt)


def dE_rot_single_sq_integral(T, idata, molecule, nokt=False):
    """Calculates the squared full averaging of dE_rot, where dE_rot is the dimenionless difference between rotational
    energies
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot, where dE_rot is the dimenionless difference between rotational energies

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule
    nokt - if True, the result is multiplied by (kT) ** (-0.5)
    """
    return (dE_rot_single(T, molecule) ** 2) * elastic_integral(T, 0, idata, nokt=nokt)


def dE_rot_c_dE_rot_d_integral(T, idata, molecule1, molecule2, nokt=False):
    """Calculates the full averaging of  dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference
    between rotational energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies
    for molecule2
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference between rotational
    energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies for molecule2

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule1 - the first molecule
    molecule2 - the second molecule2
    nokt - if True, the result is multiplied by (kT) ** (-0.5)
    """
    return dE_rot_c_dE_rot_d(T, molecule1, molecule2) * elastic_integral(T, 0, idata, nokt=nokt)


def dE_rot_dE_rot_full_integral(T, idata, molecule1, molecule2, nokt=False):
    """Calculates the full averaging of  dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference
    between rotational energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies
    for molecule2
    Considers all transitions to be one-quantum and equiprobable

    Returns:
    dE_rot_c * (dE_rot_c + dE_rot_d), where dE_rot_c is the dimenionless difference between rotational
    energies for molecule1, and dE_rot_d is the dimenionless difference between rotational energies for molecule2

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule1 - the first molecule
    molecule2 - the second molecule2
    nokt - if True, the result is multiplied by (kT) ** (-0.5)
    """
    return dE_rot_dE_rot_full(T, molecule1, molecule2) * elastic_integral(T, 0, idata, nokt=nokt)