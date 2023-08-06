"""Provides a molecule class for a state-to-state approximation. Serves as
a basis for most other modules"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from os.path import normcase, split, join


class Molecule_sts:
    """Molecule class for a state-to-state approximation
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
    current_Z_rot - current rotational partition function
    current_rae - current rotational energy averaged over the rotational spectrum
    current_rae_dim - current dimensionless rotational energy averaged over the rotational spectrum
    current_raesq - current squared rotational energy averaged over the rotational spectrum
    current_raesq_dim - current squared dimensionless rotational energy averaged over the rotational spectrum
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
        self.current_Z_rot = 0.0
        self.current_rae = 0.0
        self.current_rae_dim = 0.0
        self.current_raesq = 0.0
        self.current_raesq_dim = 0.0

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

    def renorm(self, T, T1):
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
        self.current_rot_dimless = self.rot / (constants.k * T)
        self.current_vibr_dimless = self.vibr / (constants.k * T)
        self.current_rae = self.rot_avg_energy(T, 0)
        self.current_rae_dim = self.rot_avg_energy(T, 1)
        self.current_raesq = self.rot_avg_energy_sq(T, 0)
        self.current_raesq_dim = self.rot_avg_energy_sq(T, 1)
        self.current_T = T

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

    def rot_exp(self, j, T):
        """Returns the rotational exponent: (2j + 1) * exp(-rot_energy(j) / kT), (2j + 1) being the degeneracy
        of the j-th rotational state

        Returns:
        The rotational exponent

        Takes as input:
        j - rotational level (may be an np.array of indices, result will then be an array)
        T - the temperature of the mixture
        """
        return ((2.0 * j + 1.0) / self.rot_symmetry) * np.exp(-self.rot[j] / (self.rot_symmetry * constants.k * T))

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

    def rot_avg_energy(self, T, dim=1):
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

    def rot_avg_energy_sq(self, T, dim=1):
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
            if equal to 'inf', Z_vibr_eq returns Z_vibr_eq(-infinity, 0)
            if equal to 'D6k', Z_vibr_eq returns Z_vibr_eq(-D / 6k, 0), where D is the dissociation energy of the
                               molecule
            if equal to '3T', Z_vibr_eq returns Z_vibr_eq(-3T, 0)
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