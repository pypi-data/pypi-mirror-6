"""Provides a molecule class for a multi-temperature approximation based on the Treanor distribution. Serves as
a basis for most other modules"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__version__ = "0.3.5"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from os.path import normcase, split, join


class Molecule:
    """Molecule class for a multi-temperature approximation
    Provides various methods such as averaged rotational and vibrational energies, vibrational exponents,
    dissociation-related partition functions, etc.

    Class Fields:
    name - name ('N2', 'O2', etc.)
    vibr_model - multiple options, model of vibrational energy:
        'harmonic' - a harmonic oscillator model
        'anharmonic' - an anharmonic oscillator model
        'table' - for table values of vibrational energy (if available in a separate file)
    mass - the mass
    num_rot - amount of rotational levels
    num_vibr - amount of vibrational levels (may change depending on T and T1)
    max_vibr - maximum amount of vibrational levels (during initialization this field and num_vibr are equal)
    inertia - moment of rotational inertia
    rot_const - h ^ 2 / (8 * (pi ^ 2) * inertia), used for rotational energies
    hvc - harmonicity coefficient, for vibrational energies
    avc - anharmonicity coefficient, for vibrational energies
    diss - dissociation energy
    LJe - the Lennard-Jones epsilon parameter
    LJs - the Lennard-Jones sigma parameter
    rot - array of rotational energies
    vibr - array of vibrational energies
    vibr_zero - vibrational energy of the 0-th vibrational level (since the Treanor distribution requires the energy
    of the 0th level to be considered equal to 0, the real value has to be stored separately)
    crot - specific heat capacity of rotational degrees of freedom, calculated as crot = k / molecule.mass

    All the following fields (i.e. fields which name starts with "current") are initially set to 0.0 or 1.0, and
    then updated each time the renorm method is called. They are used to store various values which depend
    on T, T1 and the numeric density of the mixture, so as to avoid calculating them twice in a row
    current_rot_dimless - array containing the current dimensionless rotational energies
    current_vibr_dimless - array containing the current dimensionless vibrational energies
    current_T - current temperature of the mixture
    current_T1 - current vibrational temperature of the particular molecular species
    current_Z_rot - current rotational partition function
    current_Z_vibr - current vibrational partition function
    current_n - current numeric density of the particular species
    current_ni - aray containing the current densities of the particular species at each vibrational level
    current_v_exp - array containing the current vibrational exponents
    current_w - current average amount of vibrational quanta of the particular species
    current_wdt - current derivative of average amount of vibrational quanta per unit of mass of the particular species
    with respect to the temperature T
    current_wdt1 - current derivative of average amount of vibrational quanta per unit of mass of the particular species
    with respect to the vibrational temperature T1
    current_edt - current derivative of vibrational energy per unit of mass of the particular species
    with respect to the temperature T
    current_edt1 - current derivative of vibrational energy per unit of mass of the particular species
    with respect to the vibrational temperature T1
    current_zdt - current derivative of vibrational partition function with respect to the temperature T
    current_zdt1 - current derivative of vibrational partition function with respect to the vibrational temperature T1
    current_vae - current vibrational energy averaged over the vibrational spectrum
    current_vae_dim - current dimensionless vibrational energy averaged over the vibrational spectrum
    current_rae - current rotational energy averaged over the rotational spectrum
    current_rae_dim - current dimensionless rotational energy averaged over the rotational spectrum
    current_vaesq - current squared vibrational energy averaged over the vibrational spectrum
    current_vaesq_dim - current squared dimensionless vibrational energy averaged over the vibrational spectrum
    current_raesq - current squared rotational energy averaged over the rotational spectrum
    current_raesq_dim - current squared dimensionless rotational energy averaged over the rotational spectrum
    current_vae - current value of i * vibrational_energy(i) averaged over the vibrational spectrum
    current_vae_dim - current value of i * dimensionless_vibrational_energy(i) averaged over the vibrational spectrum
    """
    def __init__(self, name, vmodel='anharmonic'):
        self.name = name
        self.vibr_model = vmodel
        this_dir, this_filename = split(__file__)
        raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + self.name + '.dat')))
        self.mass = raw_d[0] * constants.physical_constants['atomic mass constant'][0]
        self.num_rot = int(raw_d[1])
        self.rot_symmetry = raw_d[2]
        if vmodel == 'harmonic':
            self.num_vibr = int(raw_d[3])
            self.max_vibr = self.num_vibr
        elif vmodel == 'anharmonic' or vmodel == 'table':
            self.num_vibr = int(raw_d[4])
            self.max_vibr = self.num_vibr
        self.inertia = raw_d[5] * (10 ** (-46))
        self.rot_const = (constants.h ** 2) / (8.0 * (constants.pi ** 2) * self.inertia)
        self.hvc = raw_d[6] * 100 * constants.h * constants.c
        self.avc = raw_d[7]
        self.diss = raw_d[8] * constants.physical_constants['electron volt'][0]
        self.form = raw_d[9] * constants.physical_constants['electron volt'][0]
        self.LJe = raw_d[10]  # stored as eps/kboltz
        self.LJs = raw_d[11] * constants.physical_constants['Angstrom star'][0]
        self.rot = np.zeros(self.num_rot + 1)
        self.vibr = np.zeros(self.num_vibr + 1)
        self.vibr_zero = 0
        self.crot = constants.k / self.mass

        self.current_rot_dimless = np.zeros(self.num_rot + 1)

        self.current_T = 1.0
        self.current_T1 = 1.0
        self.current_Z_rot = 0.0
        self.current_Z_vibr = 0.0
        self.current_n = 0.0
        self.current_ni = np.zeros(self.num_vibr + 1)
        self.current_v_exp = np.zeros(self.num_vibr + 1)
        self.current_w = 0.0
        self.current_wdt = 0.0
        self.current_wdt1 = 0.0
        self.current_edt = 0.0
        self.current_edt1 = 0.0
        self.current_zdt = 0.0
        self.current_zdt1 = 0.0
        self.current_vae = 0.0
        self.current_vae_dim = 0.0
        self.current_rae = 0.0
        self.current_rae_dim = 0.0
        self.current_vaesq = 0.0
        self.current_vaesq_dim = 0.0
        self.current_raesq = 0.0
        self.current_raesq_dim = 0.0
        self.current_vae_i = 0.0
        self.current_vae_i_dim = 0.0

        a = np.arange(0, self.num_vibr + 1, 1)
        if self.vibr_model == 'table':
            try:
                f = open(normcase('data/spectra/' + self.name + '.dat'))
                f.close()
                raw_v_d = np.genfromtxt(normcase('data/spectra/' + self.name + '.dat'))
                self.vibr_zero = self.vibr[0]
                self.vibr = raw_v_d * constants.physical_constants['electron volt'][0]
                self.vibr = self.vibr - self.vibr[0]
                self.num_vibr = self.vibr.shape[0]
                self.max_vibr = self.num_vibr
            except IOError:
                print 'File with vibrational energies not found, will use anharmonic oscillator model'
                self.vibr_model = 'anharmonic'
                self.vibr_zero = 0.5 * self.hvc * (1 - 0.5 * self.avc * self.hvc)
                self.vibr[a] = self.hvc * (1.0 - self.avc) * a - self.hvc * self.avc * (a ** 2)

        elif self.vibr_model == 'anharmonic':
            self.vibr_zero = 0.5 * self.hvc * (1 - 0.5 * self.avc * self.hvc)
            self.vibr[a] = self.hvc * (1.0 - self.avc) * a - self.hvc * self.avc * (a ** 2)
        elif self.vibr_model == 'harmonic':
            self.vibr_zero = 0.5 * self.hvc
            self.vibr[a] = self.hvc * a

        self.current_vibr_dimless = np.zeros(self.num_vibr + 1)
        for j in xrange(self.num_rot + 1):
            self.rot[j] = j * (j + 1) * self.rot_const

    def renorm(self, T, T1, n_c):
        """Calculates all current values for the molecule

        Returns:
        nothing

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        n - the numeric density of the species in question
        """
        if T < T1:
            if self.avc == 0.0:
                treanor_i_star = self.num_vibr
            else:
                treanor_i_star = int(0.5 + self.vibr_energy(1, 1) * T / (2 * self.avc * self.hvc * T1))
        else:
            treanor_i_star = int(0.5 + self.vibr_energy(1, 1) * T / (2 * self.avc * self.hvc * T1))
        if self.max_vibr > treanor_i_star:
            self.num_vibr = treanor_i_star
        else:
            self.num_vibr = self.max_vibr

        self.current_Z_rot = self.Z_rot(T)
        self.current_Z_vibr = self.Z_vibr(T, T1)
        self.current_rot_dimless = self.rot / (constants.k * T)
        self.current_vibr_dimless = self.vibr / (constants.k * T)
        self.current_vae_dim = self.avg_vibr_energy(T, T1, 1)
        self.current_vae = self.avg_vibr_energy(T, T1, 0)
        self.current_rae_dim = self.avg_rot_energy(T, 1)
        self.current_rae = self.avg_rot_energy(T, 0)
        self.current_vaesq = self.avg_vibr_energy_sq(T, T1, 0)
        self.current_vaesq_dim = self.avg_vibr_energy_sq(T, T1, 1)
        self.current_raesq = self.avg_rot_energy_sq(T, 0)
        self.current_raesq_dim = self.avg_rot_energy_sq(T, 1)
        self.current_w = self.avg_i(T, T1)
        self.current_wdt = self.W_dT(T, T1)
        self.current_wdt1 = self.W_dT1(T, T1)
        self.current_edt = self.E_vibr_dT(T, T1)
        self.current_edt1 = self.E_vibr_dT1(T, T1)
        self.current_zdt = self.Z_vibr_dT(T, T1)
        self.current_zdt1 = self.Z_vibr_dT1(T, T1)
        self.current_vae_i = self.avg_vibr_energy_i(T, T1, 0)
        self.current_vae_i_dim = self.avg_vibr_energy_i(T, T1, 1)

        a = np.arange(0, self.num_vibr + 1, 1)
        self.current_v_exp = self.vibr_exp(a, T, T1)
        self.current_ni = self.ni(a, T, T1, n_c)
        self.current_n = n_c
        self.current_T = T
        self.current_T1 = T1

    def num_vibr_levels(self, true_amt=True):
        """Returns amount of vibrational levels (either the maximum one or current one)

        Returns:
        Amount of vibrational levels

        Takes as input:
        true_amt - if True, returns the current amount of vibrational levels (which is equal to or less than the
        maximum amount of vibrational levels); otherwise, return the maximum amount of vibrational levels
        """
        if true_amt is True:
            return self.num_vibr
        else:
            return self.max_vibr

    def vibr_one(self, dim=1):
        """Returns the energy of the first vibrational level (dimensionless or dimensional)

        Returns:
        The energy of the first vibrational level

        Takes as input:
        dim - if equal to 1, returns the dimensional energy of the first vibrational level; otherwise, returns the
        dimensionless energy of the first vibrational level
        """
        if dim == 1:
            return self.vibr[1]
        else:
            return self.current_vibr_dimless[1]

    def vibr_energy(self, i, dim=1):
        """Returns the energy of the i-th vibrational level (dimensionless or dimensional)

        Returns:
        The energy of the i-th vibrational level

        Takes as input:
        i - the level (may be an np.array of indices, result will then be an array)
        dim - if equal to 1, returns the dimensional energy of the i-th vibrational level; otherwise, returns the
        dimensionless energy of the i-th vibrational level

        Notes:
        if the renorm function has not been called (or called for another T than the current one), the dimensionless
        energy will be incorrect
        """
        if dim == 1:
            return self.vibr[i]
        else:
            return self.current_vibr_dimless[i]

    def rot_energy(self, j, dim=1):
        """Returns the energy of the j-th rotational level (dimensionless or dimensional)

        Returns:
        The energy of the j-th rotational level

        Takes as input:
        j - the level (may be an np.array of indices, result will then be an array)
        dim - if equal to 1, returns the dimensional energy of the j-th rotational level; otherwise, returns the
        dimensionless energy of the j-th rotational level

        Notes:
        if the renorm function has not been called (or called for another T than the current one), the dimensionless
        energy will be incorrect
        """
        if ((int(j) - j)) == 0 and (j <= self.num_rot):
            if dim == 1:
                return self.rot[j]
            else:
                return self.current_rot_dimless[j]
        else:  # non-integer values are used for integration
            if dim == 1:
                return j * (j + 1) * self.rot_const
            else:
                return j * (j + 1) * self.rot_const / (constants.k * self.current_T)

    def full_energy(self, i, j, dim=1):
        """Returns the energy of the j-th rotational level + the energy
        of the i-th vibrational level (dimensionless or dimensional)

        Returns:
        The full energy of the (i, j)-th state (i-th vibrational level and j-th rotational level)

        Takes as input:
        i - vibrational level (may be an np.array of indices, result will then be an array)
        j - rotational level (may be an np.array of indices, result will then be an array)
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy

        Notes:
        if i and j are arrays of indices, their lengths (shapes) must match!
        if the renorm function has not been called (or called for another T than the current one), the dimensionless
        energy will be incorrect
        """
        if dim == 1:
            return self.vibr[i] + self.rot[j]
        else:
            return self.current_vibr_dimless[i] + self.current_rot_dimless[j]

    def vibr_exp(self, i, T, T1):
        """Returns the vibrational exponent: exp(-(vibr_energy(i) - i * vibr_energy(1)) / kT - i * vibr_energy(1) /
        kT1)

        Returns:
        The vibrational exponent

        Takes as input:
        i - vibrational level (may be an np.array of indices, result will then be an array)
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            return np.exp(-(self.vibr[i] - i * self.vibr[1]) / (T * constants.k)
                          - i * self.vibr[1] / (T1 * constants.k))
        else:
            return self.current_v_exp[i]

    def rot_exp(self, j, T):
        """Returns the rotational exponent: (2j + 1) * exp(-rot_energy(j) / kT), (2j + 1) being the degeneracy
        of the j-th rotational state

        Returns:
        The rotational exponent

        Takes as input:
        j - rotational level (may be an np.array of indices, result will then be an array)
        T - the temperature of the mixture
        """
        return ((2.0 * j + 1.0) / self.rot_symmetry) * np.exp(-self.rot[j] / (constants.k * T))

    def Z_vibr(self, T, T1):
        """Returns the vibrational partition function Z_vibr(T, T1)

        Returns:
        The vibrational partition function

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            return self.vibr_exp(np.arange(0, self.num_vibr + 1, 1), T, T1).sum()
        else:
            return self.current_Z_vibr

    def Z_rot(self, T):
        """Returns the rotational partition function Z_rot(T)

        Returns:
        The rotational partition function

        Takes as input:
        T - the temperature of the mixture
        """
        if self.current_T != T:
            return 8.0 * (constants.pi ** 2) * self.inertia * constants.k * T / (self.rot_symmetry * (constants.h ** 2))
        else:
            return self.current_Z_rot

    def avg_rot_energy(self, T, dim=1):
        """Returns the rotational energy, averaged over the rotational spectrum (either dimensional or dimensionless)

        Returns:
        The averaged rotational energy

        Takes as input:
        T - the temperature of the mixture
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        kT = constants.k * T
        B = self.rot_const / kT
        snr = self.num_rot * (self.num_rot + 1.0)

        if dim == 1:
            return kT * (1.0 + np.exp(-B * snr) * (-B * snr - 1.0)) / (self.rot_symmetry * self.Z_rot(T) * B)
        else:
            return (1.0 + np.exp(-B * snr) * (-B * snr - 1.0)) / (self.rot_symmetry * self.Z_rot(T) * B)

    def avg_vibr_energy(self, T, T1, dim=1):
        """Returns the vibrational energy, averaged over the vibrational spectrum (either dimensional or dimensionless)

        Returns:
        The averaged vibrational energy

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            a = np.arange(0, self.num_vibr + 1, 1)
            return np.dot(self.vibr_exp(a, T, T1), self.vibr_energy(a, dim)) / self.Z_vibr(T, T1)
        else:
            if dim == 1:
                return self.current_vae_dim
            else:
                return self.current_vae

    def avg_full_energy(self, T, T1, dim=1):
        """Returns the full energy, averaged over the internal spectrum (either dimensional or dimensionless)

        Returns:
        The full internal averaged energy

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        return self.avg_vibr_energy(T, T1, dim) + self.avg_rot_energy(T, dim)

    def avg_vibr_energy_sq(self, T, T1, dim=1):
        """Returns the squared vibrational energy, averaged over the vibrational spectrum
         (either dimensional or dimensionless)

        Returns:
        The averaged squared vibrational energy

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            a = np.arange(0, self.num_vibr + 1, 1)
            return np.dot(self.vibr_exp(a, T, T1), np.power(self.vibr_energy(a, dim), 2)) / self.Z_vibr(T, T1)
        else:
            if dim == 1:
                return self.current_vaesq_dim
            else:
                return self.current_vaesq

    def avg_rot_energy_sq(self, T, dim=1):
        """Returns the squared rotational energy, averaged over the rotational spectrum
         (either dimensional or dimensionless)

        Returns:
        The averaged sqaured rotational energy

        Takes as input:
        T - the temperature of the mixture
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        if self.current_T != T:
            kT = constants.k * T
            B = self.rot_const / kT
            snr = self.num_rot * (self.num_rot + 1)
            if dim == 1:
                return (2.0 + np.exp(-B * snr) * (-B * snr * (B * snr + 2) - 2)) * (kT ** 2) / (self.rot_symmetry
                                                                                                * self.Z_rot(T) * B)
            else:
                return (2.0 + np.exp(-B * snr) * (-B * snr * (B * snr + 2) - 2)) / (self.rot_symmetry
                                                                                    * self.Z_rot(T) * B)
        else:
            if dim == 1:
                return self.current_raesq_dim
            else:
                return self.current_raesq

    def avg_i(self, T, T1):
        """Returns the average amount of vibrational quanta (returns the quantity i averaged over
         the vibrational spectrum)

        Returns:
        The average amount of vibrational quanta

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            a = np.arange(0, self.num_vibr + 1, 1)
            res = np.dot(self.vibr_exp(a, T, T1), a)
            return res / self.Z_vibr(T, T1)
        else:
            return self.current_w

    def avg_i_sq(self, T, T1):
        """Returns the squared vibrational energy level, averaged over the vibrational spectrum
         (either dimensional or dimensionless) (returns the quantity i ^ 2 averaged over the vibrational
         spectrum)

        Returns:
        The averaged squared vibrational energy level

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        """
        a = np.arange(0, self.num_vibr + 1, 1)
        res = np.dot(self.vibr_exp(a, T, T1), np.power(a, 2))
        return res / self.Z_vibr(T, T1)

    def avg_vibr_energy_i(self, T, T1, dim=1):
        """Returns the energy level multiplied by the corresponding vibrational
        energy, averaged over the vibrational spectrum
        (either dimensional or dimensionless) (returns the quantity i * vibr_energy(i) averaged over the vibrational
        spectrum)

        Returns:
        The averaged vibrational energy multiplied by the vibrational level

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species
        dim - if equal to 1, returns the dimensional energy; otherwise, returns the
        dimensionless energy
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            a = np.arange(0, self.num_vibr + 1, 1)
            return np.dot(a * self.vibr_energy(a, dim), self.vibr_exp(a, T, T1)) / self.Z_vibr(T, T1)
        else:
            if dim == 1:
                return self.current_vae_i_dim
            else:
                return self.current_vae_i

    def Z_vibr_eq(self, T, model='none'):
        """Returns the equilibrium vibrational partition function (which is used in various
        dissociation models) as a function of the temperature T and a parameter U ('model'). If U is equal to 0,
        the result is just the equilibirum partition function (except that the the vibrational energy
        at the zero level is not equal to zero); otherwise, the parameter U is used instead of the temperature T

        Returns:
        The equilibrium vibrational partition function (either as a function of T or as a function of U)

        Takes as input:
        T - the temperature of the mixture
        model - multiple options:
            if equal to 'none', Z_vibr_eq returns simply the equilibrium vibrational partition function
            if equal to 'inf', Z_vibr_eq returns Z_vibr_eq(-infinity, 'none')
            if equal to 'D6k', Z_vibr_eq returns Z_vibr_eq(-D / 6k, 'none'), where D is the dissociation energy of the
                               molecule
            if equal to '3T', Z_vibr_eq returns Z_vibr_eq(-3T, 'none')
        """

        if model == 'none':
            return np.sum(np.exp(-(self.vibr_zero + self.vibr) / (T * constants.k)))
        elif model == 'inf':
            res = 0.0
            for i in xrange(self.num_vibr + 1):
                res += 1.0
            return res
        elif model == 'D6k':
            return np.sum(np.exp(6.0 * ((self.vibr + self.vibr_zero) / self.diss)))
        elif model == '3T':
            return np.sum(np.exp((self.vibr_zero + self.vibr) / (3.0 * constants.k * T)))

    def Z_diss(self, i, T, model='D6k'):
        """Returns the non-equilibrium factor (which is used in various
        dissociation models) as a function of the temperature T and a parameter U ('model') and
        the vibrational level i, which is equal to
        Z_equilibrium(T) * exp(vibr_energy(i) * (1 / T + 1 / U) / k) / Z_equilibrium(-U)

        Returns:
        The non-equilibrium factor

        Takes as input:
        i - the vibrational level (from which the molecule dissociates)
        T - the temperature of the mixture
        model - U is equal to infiinity if model == 'inf'; U = Diss_energy / 6k if model == 'D6k';
        U = 3 * T if model == '3T'.
        model - multiple options:
            if equal to 'inf', U is equal to infinity
            if equal to 'D6k', U is equal to D / 6k, where D is the dissociation energy of the molecule
            if equal to '3T', U is equal to 3T
        """
        if model == 'inf':
            return np.exp((self.vibr[i] + self.vibr_zero) / (T * constants.k))\
                           * self.Z_vibr_eq(T, 'none') / self.Z_vibr_eq(T, model)
        elif model == 'D6k':
            return np.exp((self.vibr[i] + self.vibr_zero) * (1.0 / (constants.k * T) + 6.0 / self.diss))\
                           * self.Z_vibr_eq(T, 'none') / self.Z_vibr_eq(T, model)
        elif model == '3T':
            return np.exp((self.vibr[i] + self.vibr_zero) / (0.75 * T * constants.k)) \
                                * self.Z_vibr_eq(T, 'none') / self.Z_vibr_eq(T, model)

    def ni(self, i, T, T1, n_c):
        """Returns the numeric density at the i-th vibrational level for the molecular species, using
        the Treanor distribution for an anharmonic oscillator (or a harmonic one)

        Returns:
        The numeric density at the i-th vibrational level

        Takes as input:
        i - the vibrational level
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        n - the total numeric density of the molecular species
        """
        if (self.current_T != T) or (self.current_T1 != T1) or (self.current_n != n_c):
            return n_c * self.vibr_exp(i, T, T1) / self.Z_vibr(T, T1)
        else:
            return self.current_ni[i]

    def Z_vibr_dT(self, T, T1):
        """Returns the partial derivative of the vibrational partition function with respect to the temperature T

        Returns:
        The partial derivative of the vibrational partition function with respect to the temperature T

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            a = np.arange(0, self.num_vibr + 1, 1)
            return np.dot(self.vibr[a] - a * self.vibr[1], self.vibr_exp(a, T, T1)) / (constants.k * T * T)
        else:
            return self.current_zdt

    def Z_vibr_dT1(self, T, T1):
        """Returns the partial derivative of the vibrational partition function with respect to the vibrational
        temperature of the molecular species T1

        Returns:
        The partial derivative of the vibrational partition function with respect to the temperature T1

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            a = np.arange(0, self.num_vibr + 1, 1)
            return self.vibr[1] * np.dot(a, self.vibr_exp(a, T, T1)) / (constants.k * T1 * T1)
        else:
            return self.current_zdt1

    def W_dT(self, T, T1):
        """Returns the partial derivative of the average number of vibrational quanta per unit of mass with respect to
        the temperature T

        Returns:
        The partial derivative of the average number of vibrational quanta per unit of mass with respect to
        the temperature T

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        if self.vibr_model == 'harmonic':
                return 0.0
        else:
            if (self.current_T != T) or (self.current_T1 != T1):
                return (self.avg_vibr_energy_i(T, T1) - self.vibr[1] * self.avg_i_sq(T, T1)
                        - self.avg_i(T, T1) * self.avg_vibr_energy(T, T1) + self.vibr[1] * (self.avg_i(T, T1) ** 2))\
                        / (constants.k * T * T * self.mass)
            else:
                return self.current_wdt

    def W_dT1(self, T, T1):
        """Returns the partial derivative of the average number of vibrational quanta per unit of mass with respect to
        the vibrational temperature of the molecular species T1

        Returns:
        The partial derivative of the average number of vibrational quanta per unit of mass with respect to
        the temperature T1

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            return self.vibr[1] * (self.avg_i_sq(T, T1) - (self.avg_i(T, T1) ** 2))\
                   / (self.mass * constants.k * T1 * T1)
        else:
            return self.current_wdt1

    def E_vibr(self, T, T1):
        """Returns the full vibrational energy per unit of mass (which is equal to the averaged vibrational energy
        divided by the molecule mass)

        Returns:
        The full vibrational energy per unit of mass

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        return self.avg_vibr_energy(T, T1) / self.mass

    def E_vibr_dT(self, T, T1):
        """Returns the partial derivative of the full vibrational energy per unit of mass with respect to
        the temperature T

        Returns:
        The partial derivative of the full vibrational energy per unit of mass with respect to
        the temperature T

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            if self.vibr_model == 'harmonic':
                return 0.0
            else:
                return ((self.avg_vibr_energy_sq(T, T1) - (self.avg_vibr_energy(T, T1) ** 2))
                        + self.vibr[1] * (self.avg_i(T, T1) * self.avg_vibr_energy(T, T1) - self.avg_vibr_energy_i(T, T1)))\
                        / (constants.k * T * T * self.mass)
        else:
            return self.current_edt

    def E_vibr_dT1(self, T, T1):
        """Returns the partial derivative of the full vibrational energy per unit of mass with respect to
        the vibrational temperature of the molecular species T1

        Returns:
        The partial derivative of the full vibrational energy per unit of mass with respect to
        the temperature T1

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        """
        if (self.current_T != T) or (self.current_T1 != T1):
            return (self.avg_vibr_energy_i(T, T1) - self.avg_i(T, T1) * self.avg_vibr_energy(T, T1))\
                    * self.vibr[1] / (self.mass * constants.k * T1 * T1)
        else:
            return self.current_edt1

    def avg_vibr_f(self, T, T1, f, *args):
        """Performs vibrational averaging of a function dependent on the vibrational level (and other parameters)
        The function should be of the following form : f(*args1, i, *args2), where
        *args1 are some arguments, i is the vibrational level, *args2 are the rest arguments
        Summation is performed over the variable i, so make sure that it corresponds to the vibrational level

        Returns:
        The vibrational averaging of a function dependent on the vibrational level (and other parameters)

        Takes as input:
        T - the temperature of the mixture
        T1 - the vibrational temperature of the molecular species in question
        f - the function to be averaged
        *args - the parameters of the function (apart from the index i which corresponds to the vibrational level)

        Notes:
        This isn't the most useful code, since all the possibly needed averaged quantities are available as faster
        routines, but it's pretty, so it stays.
        """
        res = 0
        f_n = f.func_code.co_varnames
        if 'i' in f_n:
            i_pos = f_n.index('i')
            l_args = list(args)
            l_args.insert(i_pos, 0)
            for i in xrange(self.num_vibr + 1):
                l_args[i_pos] = i
                args = tuple(l_args)
                res += self.vibr_exp(i, T, T1) * f(*args)
            return res / self.Z_vibr(T, T1)
        else:
            return f(*args)