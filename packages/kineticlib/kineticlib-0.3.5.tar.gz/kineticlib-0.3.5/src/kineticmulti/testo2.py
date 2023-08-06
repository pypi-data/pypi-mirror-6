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

O2 = molecule.Molecule('O2', 'anharmonic')

# print N2.diss
#
# for i in enumerate(N2.vibr):
#     print 've(' + str(i[0]) + ') = ' + str(i[1])


n = 100000.0 / (2000.0 * constants.k)

p = 100000.0
O2.renorm(2000.0, 2000.0, p / (2000.0 * constants.k))

print O2.diss
# print O2.rot[O2.num_rot]
# print O2.rot_energy(O2.num_rot)
# print O2.vibr_energy(O2.num_vibr)
print O2.vibr[O2.num_vibr]
print '\n'
T = 2000.0
# print N2.Z_vibr(2000.0, 2000.0)
# print O2.Z_vibr(10000.0, 10000.0)
print O2.Z_rot(2000.0)
q = 0.0
for i in xrange(O2.num_rot + 1):
    q += O2.rot_exp(i, T)
    # if i % 2 == 0:
    #     q += (1.0 / 1.0) * O2.rot_exp(i, T)
    # else:
    #     q += (1.0 / 3.0) * O2.rot_exp(i, T)
print 'real', q
print 'full Z_int', O2.Z_rot(2000.0) * O2.Z_vibr(2000.0, 2000.0)
print '\n'

T = 10000.0
print 'T =', T
O2.renorm(T, T, p / (T * constants.k))
print O2.Z_rot(T)
q = 0.0
for i in xrange(O2.num_rot + 1):
    q += O2.rot_exp(i, T)
    # if i % 2 == 0:
    #     q += (1.0 / 1.0) * O2.rot_exp(i, T)
    # else:
    #     q += (1.0 / 3.0) * O2.rot_exp(i, T)
print 'real', q
print 'full Z_int', O2.Z_rot(T) * O2.Z_vibr(T, T)

