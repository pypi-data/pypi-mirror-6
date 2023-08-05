

from setuptools import setup,find_packages
from myhdl_tools import __version__

# The README is probably a little too long for the
# pipy stuff.
desc= \
"""
This Python package contains a mix-mash of tools to assist 
MyHDL designs.  Includes common components and scripts that 
are frequently used in complex digital designs.  The tools
assist in automating FPGA toolflows, simulations, and 
cosimulation.
"""

setup(name='myhdl_tools',
      version=__version__,
      author="Christopher Felton",
      author_email="chris.felton@gmail.com",
      license="LGPL",
      description="random collection of tools to support myhdl",
      keywords="myhdl FPGA tools",
      url="https://bitbucket.org/cfelton/myhdl_tools",
      packages = find_packages(),
      long_description=desc,
      test_suite = 'nose.collector',
      tests_require = 'nose',      
      )
