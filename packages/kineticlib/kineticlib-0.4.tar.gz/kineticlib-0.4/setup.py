from distutils.core import setup

setup(name='kineticlib',
      version='0.4',
      description='Library for kinetic theory calculations in the multi-temperature and state-to-state approximations',
      author='George Oblapenko',
      author_email='kunstmord@kunstmord.com',
      url='https://github.com/Kunstmord/kineticlib',
      license="GPL",
      packages=['kineticlib'],
      package_dir={'kineticlib': 'src/kineticmulti'},
      package_data={'kineticlib': ['data/models/*.csv', 'data/particles/*.dat', 'data/spectra/*.dat']},
      requires=['numpy', 'scipy'],
      include_package_data=True
      )