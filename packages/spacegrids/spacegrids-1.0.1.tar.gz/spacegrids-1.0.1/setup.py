#from distutils.core import setup
from setuptools import setup, find_packages

with open('README.rst') as file:
        long_description = file.read()

setup(name='spacegrids',
      version='1.0.1',
      author='Willem Sijp',
      author_email='w.sijp@unsw.edu.au',
      description='numpy array with grids and associated operations',
      keywords=('climate data','grid data','data on grids'),
      packages = find_packages(exclude="tests"),
      package_data = {
	  "spacegrids": ['README.rst']
	  },
      long_description=long_description,
      url='https://github.com/willo12/spacegrids',
      license = "BSD"
#      install_requires = ["numpy>=1.7"]
#      extras_require = {
#	  "ncio": ["netCDF4>=1.0.6"],
#	  "pandas": ["pandas>=0.8.0"],
#	  "plotting": ["pandas>=0.8.0","matplotlib>=1.2.1"],
#	  "interp2d": ["basemap>=1.06"],
#	  }
      )
