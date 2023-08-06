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

N2 = molecule.Molecule('N2', 'table')

# print N2.diss
#
# for i in enumerate(N2.vibr):
#     print 've(' + str(i[0]) + ') = ' + str(i[1])


n = 100000.0 / (2000.0 * constants.k)

dat = omegaint.load_interaction(N2, N2)
print N2.num_vibr
# q = omegaint.omega(1000.0, 2, 1, dat, 'VSS')

q = cs_new.vt_integral(1000.0, 1, dat, N2, 30, -1)
print q

N2_sts = molecule_sts.Molecule('N2', 'table')
dat = omegaint.load_interaction(N2_sts, N2_sts)
q = cs_new.vt_integral(1000.0, 1, dat, N2_sts, 30, -1)
print q
#
# print N2.vibr_one() / (2000.0 * constants.k)
#
# print wtpoly.Y_poly_norm(2000.0, 2000.0, N2, 0.01)
# print wtpoly.Y_poly_norm(2000.0, 2000.0, N2, 100.01)
#
# a = np.arange(0.0001, 1000.0, 0.1)
# b = np.zeros(a.shape[0])
# for i in enumerate(a):
#     b[i[0]] = wtpoly.Y_poly_norm(2000.0, 2000.0, N2, a[i[0]])
# plt.plot(a, b)
# plt.show()