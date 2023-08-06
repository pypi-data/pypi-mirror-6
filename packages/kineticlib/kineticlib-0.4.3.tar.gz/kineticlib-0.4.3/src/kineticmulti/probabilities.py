"""Contains functions for calculating VV and VT transition probabilities

TODO3: Check VV probability? (Looks incorrect for multi-quantum transitions)
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"

import numpy as np
from scipy import constants
from scipy.misc import factorial


def fact_div_fact(start, end):
    """
    Helper function, returns end! / (end - start)!, where s and e are integers. This is faster than using the factorial
    routine in SciPy

    Returns:
    A product of all numbers from start to end

    Takes as input:
    start - positive integer, starting point of the sequence
    end - positive integer, ending point of the seqence
    """
    return np.prod(np.arange(start + 1.0, end + 1.0, 1.0))


def vel_avg_vt(g, ve_i1, ve_i2, m):
    """Helper function, returns the arithmetic mean of the relative velocity of particles before and after
    a VT transition (using the energy conservation law) M(i1) + P -> M(i2) + P

    Returns:
    Arithmetic mean of before- and after- velocities for a VT transition

    Takes as input:
    g - relative velocity before the collision
    ve_i1 - vibrational energy of level i1 of the molecule (before transition)
    ve_i2 - vibrational energy of level i2 of the molecule 1 (after transition)
    m - collision-reduced mass

    Notes:
    If the square of the after-collision velocity is < 0, then the collision is impossible for such parameters and
    the function returns -1
    """
    gn_sq = (ve_i1 - ve_i2) * (2.0 / m) + (g ** 2)
    if gn_sq < 0:
        return -1
    else:
        return 0.5 * (g + (gn_sq ** 0.5))


def vel_avg_vv(g, ve_i1, ve_k1, ve_i2, ve_k2, m):
    """Helper function, returns the arithmetic mean of the relative velocity of particles before and after
    a VV transition (using the energy conservation law) M1(i1) + M2(k1) -> M1(i2) + M2(k2)

    Returns:
    Arithmetic mean of before- and after- velocities for a VV transition

    Takes as input:
    g - relative velocity before the collision
    ve_i1 - vibrational energy of level i1 of molecule 1 (before transition)
    ve_k1 - vibrational energy of level k1 of molecule 2 (before transition)
    ve_i2 - vibrational energy of level i2 of molecule 1 (after transition)
    ve_k2 - vibrational energy of level k2 of molecule 2 (after transition)
    m - collision-reduced mass

    Notes:
    If the square of the after-collision velocity is < 0, then the collision is impossible for such parameters and
    the function returns -1
    """
    gn_sq = (ve_i1 - ve_i2 + ve_k1 - ve_k2) * (2.0 / m) + (g ** 2)
    if gn_sq < 0:
        return -1
    else:
        return 0.5 * (g + (gn_sq ** 0.5))


def vt_probability(g, T, idata, molecule, i, delta):
    """Returns the probability of a VT transition using the FHO (Forced harmonic oscillator) model
     M(i) + P -> M(i + delta) + P

    Returns:
    VT transition probability

    Takes as input:
    g - dimensionless relative velocity before the collision
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the molecule undergoing the VT transition
    i - the vibrational level of the molecule before the collision
    delta - the change in the vibrational level
    """
    svt = 0.5

    if delta > 0:
        s = delta * 1.0
        ns = fact_div_fact(i, i + delta)
    else:
        s = -delta * 1.0
        ns = fact_div_fact(i + delta, i)

    omega = np.absolute((molecule.vibr[i] - molecule.vibr[i + delta]) / delta) / constants.hbar
    if omega == 0.0:
        return 0.0
    g *= (2 * constants.k * T / idata[0]) ** 0.5  # convert to dimensional velocity
    vel = vel_avg_vt(g, molecule.vibr[i], molecule.vibr[i + delta], idata[0])

    if vel < 0.0:
        return 0.0
    phi = 2.0 * np.arctan(((2.0 * (molecule.diss + molecule.vibr_zero) / idata[0]) ** 0.5) / vel)

    eps = (np.cosh((1.0 + phi) * omega / (idata[4] * vel))
           / (np.sinh(2.0 * constants.pi * omega / (idata[4] * vel)))) ** 2
    eps *= 4.0 * svt * (constants.pi ** 2) * omega * idata[0] / ((idata[4] ** 2) * constants.h)
    prob = ns * (eps ** s) * np.exp(- 2.0 * (ns ** (1.0 / s)) * eps / (s + 1)) / (factorial(s) ** 2)
    return prob


def vt_prob_g_only(g, T, idata, vibr_spec, i, delta, depth):
    """Returns the probability of a VT transition using the FHO (Forced harmonic oscillator) model
     M(i) + P -> M(i + delta) + P

    Returns:
    VT transition probability

    Takes as input:
    g - dimensionless relative velocity before the collision
    T - the temperature of the mixture
    idata - collision data for the species involved
    vibr_spec1 - vibrational spectrum of the molecule
    i - the vibrational level of the molecule before the collision
    delta - the change in the vibrational level
    depth - potential well depth of the molecule
    """
    svt = 0.5

    g *= (2 * constants.k * T / idata[0]) ** 0.5  # convert to dimensional velocity
    vel = vel_avg_vt(g, vibr_spec[i], vibr_spec[i + delta], idata[0])
    if vel < 0.0:
        return 0.0

    if delta == 1:
        omega = (vibr_spec[i + 1] - vibr_spec[i]) / constants.hbar
        phi = 2.0 * np.arctan(((2.0 * depth / idata[0]) ** 0.5) / vel)

        eps = (np.cosh((1.0 + phi) * omega / (idata[4] * vel))
               / (np.sinh(2.0 * constants.pi * omega / (idata[4] * vel)))) ** 2
        eps *= 4.0 * svt * (constants.pi ** 2) * omega * idata[0] / ((idata[4] ** 2) * constants.h)
        return eps * np.exp(-(i + 1) * eps)
    elif delta == -1:
        omega = (vibr_spec[i] - vibr_spec[i - 1]) / constants.hbar
        phi = 2.0 * np.arctan(((2.0 * depth / idata[0]) ** 0.5) / vel)

        eps = (np.cosh((1.0 + phi) * omega / (idata[4] * vel))
               / (np.sinh(2.0 * constants.pi * omega / (idata[4] * vel)))) ** 2
        eps *= 4.0 * svt * (constants.pi ** 2) * omega * idata[0] / ((idata[4] ** 2) * constants.h)
        return eps * np.exp(-i * eps)
    elif delta > 0:
        s = delta * 1.0
        omega = (vibr_spec[i + delta] - vibr_spec[i]) / (delta * constants.hbar)
        ns = fact_div_fact(i, i + delta)
        phi = 2.0 * np.arctan(((2.0 * depth / idata[0]) ** 0.5) / vel)
        eps = (np.cosh((1.0 + phi) * omega / (idata[4] * vel))
               / (np.sinh(2.0 * constants.pi * omega / (idata[4] * vel)))) ** 2
        eps *= 4.0 * svt * (constants.pi ** 2) * omega * idata[0] / ((idata[4] ** 2) * constants.h)
        return (eps ** s) * np.exp(- 2.0 * (ns ** (1.0 / s)) * eps / (s + 1))
    else:
        s = -delta * 1.0
        omega = (vibr_spec[i + delta] - vibr_spec[i]) / (delta * constants.hbar)
        ns = fact_div_fact(i + delta, i)
        phi = 2.0 * np.arctan(((2.0 * depth / idata[0]) ** 0.5) / vel)
        eps = (np.cosh((1.0 + phi) * omega / (idata[4] * vel))
               / (np.sinh(2.0 * constants.pi * omega / (idata[4] * vel)))) ** 2
        eps *= 4.0 * svt * (constants.pi ** 2) * omega * idata[0] / ((idata[4] ** 2) * constants.h)
        return (eps ** s) * np.exp(- 2.0 * (ns ** (1.0 / s)) * eps / (s + 1))


def vv_probability(g, T, idata, molecule1, molecule2, i, k, i_delta):
    """Returns the probability of a VV transition using the FHO (Forced harmonic oscillator) model
     M1(i) + M2(k) -> M1(i + delta) + M2(k - i_delta)

    Returns:
    VV transition probability

    Takes as input:
    g - dimensionless relative velocity before the collision
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule1 - the first molecule undergoing the VV transition
    molecule2 - the second molecule undergoing the VV transition
    i - the vibrational level of the first molecule before the collision
    k - the vibrational level of the second molecule before the collision
    i_delta - the change in the vibrational level of the first molecule
    """
    svv = 0.04

    if i_delta > 0:
        s = i_delta * 1.0
        ns1 = fact_div_fact(i, i + i_delta)
        ns2 = fact_div_fact(k - i_delta, k)
    else:
        s = -i_delta * 1.0
        ns1 = fact_div_fact(i + i_delta, i)
        ns2 = fact_div_fact(k, k - i_delta)

    g *= (2.0 * constants.k * T / idata[0]) ** 0.5
    vel = vel_avg_vv(g, molecule1.vibr[i], molecule2.vibr[k], molecule1.vibr[i + i_delta], molecule2.vibr[k - i_delta],
                     idata[0])

    if vel < 0:
        return 0.0
    omega1 = np.absolute((molecule1.vibr[i] -
                          molecule1.vibr[i + i_delta]) / i_delta) / constants.hbar

    omega2 = np.absolute((molecule2.vibr[k] -
                          molecule2.vibr[k - i_delta]) / i_delta) / constants.hbar

    if omega1 == 0.0 or omega2 == 0:
        return 0.0
    xi = 2 * np.abs(omega1 - omega2) / (idata[4] * vel)
    if xi < 1.0 ** (-4):
        rhoxi = 0.25 * svv * ((idata[4] * vel) ** 2) / (omega1 * omega2)
    else:
        rhoxi = svv * (np.abs(omega1 - omega2) ** 2) / (omega1 * omega2 * (np.sinh(xi) ** 2))

    return rhoxi * ns1 * ns2 * np.exp(-2.0 * rhoxi * ((ns1 * ns2) ** (1.0 / s)) / (s + 1)) / (factorial(s) ** 2)


def vv_prob_g_only(g, T, idata, vibr_spec1, vibr_spec2, i, k, i_delta):
    """Returns the velocity-dependent part of the VV transition probability using the FHO (Forced harmonic oscillator)
     model: M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta) (for use in integration - less calculations are performed;
     stuff that doesn't depend on velocity can be calculated once in the integration procedure)

    Returns:
    Velocity-dependent part of the VV transition probability

    Takes as input:
    g - dimensionless relative velocity before the collision
    T - the temperature of the mixture
    idata - collision data for the species involved
    vibr_spec1 - vibrational spectrum of the first molecule
    vibr_spec2 - vibrational spectrum of the second molecule
    i - the vibrational level of the first molecule before the collision
    k - the vibrational level of the second molecule before the collision
    i_delta - the change in the vibrational level of the first molecule (should be > 0)
    """
    svv = 0.04
    g *= (2.0 * constants.k * T / idata[0]) ** 0.5
    vel = vel_avg_vv(g, vibr_spec1[i], vibr_spec2[k], vibr_spec1[i + i_delta], vibr_spec2[k - i_delta], idata[0])
    if vel < 0:
        return 0.0

    if i_delta == 1:
        omega1 = (vibr_spec1[i + 1] - vibr_spec1[i]) / constants.hbar
        omega2 = (vibr_spec2[k] - vibr_spec2[k - 1]) / constants.hbar
        xi = 2.0 * np.abs(omega1 - omega2) / (idata[4] * vel)
        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * svv * ((idata[4] * vel) ** 2) / (omega1 * omega2)
        else:
            rhoxi = svv * ((omega1 - omega2) ** 2) / (omega1 * omega2 * (np.sinh(xi) ** 2))

        return rhoxi * np.exp(-((i + 1) * k) * rhoxi)
    elif i_delta == -1:
        omega1 = (vibr_spec1[i] - vibr_spec1[i - 1]) / constants.hbar
        omega2 = (vibr_spec2[k + 1] - vibr_spec2[k]) / constants.hbar

        xi = 2.0 * np.abs(omega1 - omega2) / (idata[4] * vel)
        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * svv * ((idata[4] * vel) ** 2) / (omega1 * omega2)
        else:
            rhoxi = svv * ((omega1 - omega2) ** 2) / (omega1 * omega2 * (np.sinh(xi) ** 2))

        return rhoxi * np.exp(-(i * (k + 1)) * rhoxi)
    elif i_delta > 0:
        s = i_delta * 1.0

        omega1 = (vibr_spec1[i + i_delta] - vibr_spec1[i]) / (i_delta * constants.hbar)
        omega2 = (vibr_spec2[k] - vibr_spec2[k - i_delta]) / (i_delta * constants.hbar)

        xi = 2.0 * np.abs(omega1 - omega2) / (idata[4] * vel)
        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * svv * ((idata[4] * vel) ** 2) / (omega1 * omega2)
        else:
            rhoxi = svv * (np.abs(omega1 - omega2) ** 2) / (omega1 * omega2 * (np.sinh(xi) ** 2))

        return rhoxi * np.exp(-2.0 * ((fact_div_fact(i, i + i_delta) * fact_div_fact(k - i_delta, k)) ** (1.0 / s))
                     * rhoxi / (s + 1))
    else:
        s = -i_delta * 1.0

        omega1 = (vibr_spec1[i + i_delta] - vibr_spec1[i]) / (i_delta * constants.hbar)
        omega2 = (vibr_spec2[k] - vibr_spec2[k - i_delta]) / (i_delta * constants.hbar)

        xi = 2.0 * np.abs(omega1 - omega2) / (idata[4] * vel)
        if xi < 1.0 ** (-10):
            rhoxi = 0.25 * svv * ((idata[4] * vel) ** 2) / (omega1 * omega2)
        else:
            rhoxi = svv * (np.abs(omega1 - omega2) ** 2) / (omega1 * omega2 * (np.sinh(xi) ** 2))

        return rhoxi * np.exp(-2.0 * ((fact_div_fact(i + i_delta, i) * fact_div_fact(k, k - i_delta)) ** (1.0 / s))
                     * rhoxi / (s + 1))