"""Contains functions for calculating VV- and VT- rates
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"


from crosssection import vv_integral, vt_integral


def vt_rate(T, idata, molecule, i, delta):
    """Calculates the VT transition rate using the FHO probability and VSS cross-section models for
    the following process: M1(i) + P -> M1(i + delta) + P

    Returns:
    VT transition rate

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule - the fmolecule undergoing the VT transition
    i - the vibrational level of the molecule
    delta - by what value the vibrational level is changed
    """
    return 8.0 * vt_integral(T, 0, idata, molecule, i, delta, False)


def vv_rate(T, idata, molecule1, molecule2, i, k, i_delta):
    """Calculates the VV otransition rate the FHO probability and VSS cross-section models for
    the following process: M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)

    Returns:
    VV transition rate

    Takes as input:
    T - the temperature of the mixture
    idata - collision data for the species involved
    molecule1 - the first molecule undergoing the VV transition
    molecule2 - the second molecule undergoing the VV transition
    i - the vibrational level of the first molecule
    k - the vibrational level of the second molecule
    i_delta - by what value the vibrational level of the first molecule is changed
    """
    return 8.0 * vv_integral(T, 0, idata, molecule1, molecule2, i, k, i_delta, False)
#
#
# def billing_nitrogen_vt_rate(T, name1, name2, i, i_delta):
#     """Calculates the VT transition rate for a collision involving molecular nitrogen based on Billing's
#     approximation of exact trajectory calculations: either N2(i) + N2 -> N2(i - 1) + N2
#     or N2(i) + N -> N2(i + i_delta) + N
#
#     Returns:
#     VT transition rate
#
#     Takes as input:
#     T - the temperature of the mixture
#     name1 - name of the first collision partner, a string
#     name2 - name of the second collision partner, a string
#     i - the vibrational level of the molecule
#     i_delta - by what value the vibrational level is changed (taken into account only for N2 + N collisions, for
#     a N2 + N2 collision is equal to -1)
#     """
#     if name1 == 'N2' and name2 == 'N2':
#         k10 = np.exp(-3.24093 - (140.69597 / (T ** 0.2)))
#         deltaVT = 0.26679 - 6.99237 * (10 ** (-5)) * T + 4.70073 * (10 ** (-9)) * (T ** 2)
#         return (10 ** (-9)) * i * k10 * np.exp(deltaVT * (i - 1))
#     elif (name1 == 'N2' and name2 == 'N') or (name1 == 'N' and name2 == 'N2'):  # N2N rate
#         b0 = -25.708 - 5633.1543 / T
#         b1 = -0.1554 + 111.3426 / T
#         b2 = 0.0054 - 2.189 / T
#         c0 = 0.0536 + 122.4835 / T
#         c1 = 0.0013 - 4.2365 / T
#         c2 = -1.197 * 0.0001 + 0.0807 / T
#         return (10 ** (-9)) * np.exp(b0 + b1 * i_delta + b2 * (i_delta ** 2) + i * (c0 + c1 * i_delta + c2 * (i_delta ** 2)))
#     else:
#         return -1