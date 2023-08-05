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

from myhdl import Signal,intbv
from ... import Clock,Reset
from ..._xilinx import XilinxFPGA

atlys = XilinxFPGA('atlys')
atlys.add_port('clock', Clock(0, frequency=50e6), pins=('L15',))

# on-board LEDs
atlys.add_port('led', Signal(intbv(0)[8:]),
               pins=('U18', 'M14', 'N14', 'L14',
                     'M13', 'D4',  'P16', 'N12'))
# on-board push buttons
atlys.add_port('btn', Signal(intbv(0)[8:]),
               pins=('T15', 'N4', 'P4', 'P3',
                     'F6', 'F5',))
# device
atlys.set_device('spartan6', 'XC6SLX45', 'CSG324', '-5')
