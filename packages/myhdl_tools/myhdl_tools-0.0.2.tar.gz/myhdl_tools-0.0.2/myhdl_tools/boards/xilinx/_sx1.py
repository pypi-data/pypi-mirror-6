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

# SX1 Board
sx1 = XilinxFPGA('sx1')
sx1.add_port('clock', Clock(0, frequency=48e6), pins=(35,))
sx1.add_port('reset', Reset(0,active=0,async=True), pins=(13,))
sx1.add_port('led', Signal(intbv(0)[7:]), pins=(90,91,92,94,95,96,99))
sx1.set_device('spartan3e', 'XC3S500E', 'vq100', '-5')
