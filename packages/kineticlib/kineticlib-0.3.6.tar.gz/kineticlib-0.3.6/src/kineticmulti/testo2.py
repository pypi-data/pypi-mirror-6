import molecule as mol
from scipy import constants
from scipy.integrate import quad
import atom
import omegaint
import loaddata
import reltimes
import numpy as np
import ratesvibr
import matplotlib.pyplot as plt


def main():
    N2 = mol.Molecule('N2', 'anharmonic')
    N = atom.Atom('N')
    p = 100000.0
    N2.renorm(2000.0, 2000.0, p / (2000.0 * constants.k))
    N2N_idata = loaddata.load_elastic_parameters(N2, N)

    e_T = 35000.0
    s_T = 1000.0

    T_step = 200.0

    e_T += T_step

    n_steps = int((e_T - s_T) / T_step)

    rdef = np.zeros(n_steps)
    rpark = np.zeros(n_steps)
    T = s_T - T_step

    for i in xrange(n_steps):
        T += T_step
        n = p / (T * constants.k)
        N2.renorm(T, T, n)
        rpark[i] = reltimes.rot_rel_time(T, N2N_idata, n, 15.3)
        rdef[i] = reltimes.rot_tel_time_def(T, N2N_idata, N2, n)

    plt.plot(rpark, 'g*')
    plt.plot(rdef, 'k.')
    plt.show()

if __name__ == '__main__':
    main()
