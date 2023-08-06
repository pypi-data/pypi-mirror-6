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

print N2.rot_const / constants.k

print N2.diss
print N2.num_rot
print N2.rot_energy(N2.num_rot + 1)
print '\n'
T = 2000.0
# print N2.Z_vibr(2000.0, 2000.0)
# print N2.Z_vibr(10000.0, 10000.0)
print N2.Z_rot(2000.0)
q = 0.0
for i in xrange(N2.num_rot + 1):
    if i % 2 == 0:
        q += (2.0 / 3.0) * N2.rot_exp(i, T)
    else:
        q += (1.0 / 3.0) * N2.rot_exp(i, T)
print 'real', q
print 'full Z_int', N2.Z_rot(2000.0) * N2.Z_vibr(2000.0, 2000.0)
print '\n'

T = 10000.0
print 'T =', T
N2.renorm(T, T, p / (T * constants.k))
print N2.Z_rot(T)
q = 0.0
for i in xrange(N2.num_rot + 1):
    if i % 2 == 0:
        q += (2.0 / 3.0) * N2.rot_exp(i, T)
    else:
        q += (1.0 / 3.0) * N2.rot_exp(i, T)
print 'real', q
print 'full Z_int', N2.Z_rot(T) * N2.Z_vibr(T, T)

