"""Test/compare"""
__author__ = 'georgeoblapenko'


import wtpoly
import molecule
import molecule_sts
import numpy as np
import crosssection as cs_new
import omegaint
from time import clock
from scipy import constants
import matplotlib.pyplot as plt
import loaddata

N2 = molecule.Molecule('N2', 'anharmonic')

# print N2.diss
#
# for i in enumerate(N2.vibr):
#     print 've(' + str(i[0]) + ') = ' + str(i[1])


n = 100000.0 / (2000.0 * constants.k)

p = 100000.0
N2.renorm(2000.0, 2000.0, p / (2000.0 * constants.k))

T = 2000.0

print N2.Z_vibr_dT1(T, T)
print (N2.Z_vibr(T, T + 1.0) - N2.Z_vibr(T, T))
print N2.E_vibr_dT(T, T)
print (N2.E_vibr(T + 1.0, T) - N2.E_vibr(T, T))
print N2.E_vibr_dT1(T, T)
print 100 * (N2.E_vibr(T, T + 0.01) - N2.E_vibr(T, T))
# print N2.E_vibr_dT_new(2000.0, 2000.0)

