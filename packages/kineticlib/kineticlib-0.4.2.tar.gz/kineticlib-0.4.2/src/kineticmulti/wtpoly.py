"""Contains functions for working with Waldman-Trubenbacher polynomials
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"


def Y_poly_norm(T, T1, molecule, F):
    """Calculates the square of the "norm" of the Waldman Trubenbacher polynomial of the following form:
    Y_{ij} = -[energy(i, j) / kT - i * F]', where the i is the vibrational level of the molecule,
    j is the rotational level of the molecule, energy(i, j) is the full internal energy at these levels,
    [A]' = A - <A>, where <> denotes averaging over the internal spectrum. The square of the "norm" is defined as:
    ||Y_ij|| = <Y_{ij} ^ 2>

    Returns:
    The square of the "norm" of the Waldman Trubenbacher polynomial

    Takes as input:
    T - the temperature of the mixture
    T1 - the vibrational temperature of the molecule for which the polynomial is calculated
    molecule - the molecule for which the polynomial is being calculated
    F - a constant
    """
    return molecule.avg_vibr_energy_sq(T, T1, 0) + molecule.avg_rot_energy_sq(T, 0)\
                                                 + molecule.avg_i_sq(T, T1) * (F ** 2)\
                                                 + 2 * molecule.avg_vibr_energy(T, T1, 0)\
                                                     * molecule.avg_rot_energy(T, 0)\
                                                 - 2 * molecule.avg_vibr_energy_i(T, T1, 0) * F\
                                                 - 2 * molecule.avg_rot_energy(T, 0) * molecule.avg_i(T, T1) * F\
                                                 - (Y_simple_avg(T, T1, molecule, F) ** 2)


def Y_simple_avg(T, T1, molecule, F):
    """Calculates the averaging over the internal energy spectrum of the following expression:
    energy(i, j) / kT - i * F

    Returns:
    The averaging over the internal energy spectrum Waldman Trubenbacher polynomial

    Takes as input:
    T - the temperature of the mixture
    T1 - the vibrational temperature of the molecule for which the polynomial is calculated
    molecule - the molecule for which the polynomial is being calculated
    F - a constant
    """
    return molecule.avg_full_energy(T, T1, 0) - molecule.avg_i(T, T1) * F