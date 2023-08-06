"""Provides an atom class. Serves as a basis for most other modules"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from os.path import normcase, join, split


class Atom(object):
    """Atom class
    Holds the basic information - name, mass, Lennard-Jones epsilon and sigma parameters, and the formation energy.

    Class Fields:
    mass - the mass
    LJe - the Lennard-Jones epsilon parameter
    LJs - the Lennard-Jones epsilon parameter
    form - the formation energy

    Has NO methods (why would it need any, anyway?)
    """
    def __init__(self, name):
        self.name = name
        this_dir, this_filename = split(__file__)
        raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + self.name + '.dat')))
        self.mass = raw_d[0] * constants.physical_constants['atomic mass constant'][0]
        self.LJe = raw_d[1]
        self.LJs = raw_d[2] * constants.physical_constants['Angstrom star'][0]
        self.form = 0.5 * raw_d[3] * constants.physical_constants['electron volt'][0]
