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

# UFO400 Boards
ufo400 = XilinxFPGA('ufo400')
ufo400.add_port('clock', Clock(0, frequency=48e6), pins=(124,))
ufo400.add_port('reset', Reset(0,active=0,async=True), pins=(8,))
ufo400.add_port('led', Signal(intbv(0)[8:]), 
                pins=(92,93,95,96,97,98,99,100))
ufo400.set_device('spartan3', 'XC3S400', 'tq144', '-5')

