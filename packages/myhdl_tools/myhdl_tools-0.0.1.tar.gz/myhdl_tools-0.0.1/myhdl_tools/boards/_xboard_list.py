#
# Copyright (c) 2013 Christopher Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The following is a collection of different Xilinx based FPGA
development boards.  The defualt pin names (from schematics)
is defined.  If an HDL top-level matches the hardware pin
names no ports need to be defined.

For each pin defined for the hardware a port can be defined,
the tools will map the HDL top-level ports to the ports defined
below or the ports can be overridden with the HDL names, see
examples for port redefinitions
"""

# list of boards with default pin mappings

# import the xilinx based FPGA board definitions
from xilinx import xula,xula2
from xilinx import nexys
from xilinx import atlys
from xilinx import xupv2p
from xilinx import ufo400
from xilinx import sx1


# Board list
xbrd = {
    'ufo400': ufo400,  # spartan3
    'sx1': sx1,        # spartan3e with audio codec

    # digilent boards
    'nexys': nexys,    # digilent spartan3 board
    'atlys': atlys,    # digilent spartan6 board

    'xupv2p': xupv2p,  # virtex II board

    # Xess corp boards
    'xula': xula,      # spartan3 mod board
    'xula2': xula2     # spartan6 
    }
        
def get_xilinx_board(name=None, top=None, path='./xilinx/'):
    brd = None
    if xbrd.has_key(name):
       brd = xbrd[name]
    else:
        # @todo: look at a name and determine if it is close to one
        #        of the existing boards and provide a suggestion
        print('boards: %s'%(str(xbrd.keys)))
        raise ValueError('Invalid board %s'%(name))

    if top is not None:
        brd.set_top(top)
    brd.path = path

    return brd
