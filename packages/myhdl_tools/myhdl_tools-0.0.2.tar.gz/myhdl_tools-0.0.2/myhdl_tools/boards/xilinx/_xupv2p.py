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


# XUPV2P board (provided by Jos Huisken)
xupv2p = XilinxFPGA('xupv2p')
xupv2p.add_port('clock', Clock(0, frequency=100e6), pins=('AJ15',))
xupv2p.add_port('reset', Reset(0, active=0, async=True), pins=('AH5',))
xupv2p.add_port('led', Signal(intbv(0)[4:]),
               pins=('AC4','AC3','AA6','AA5'))
xupv2p.set_device('virtex2p','XC2VP30','ff896','-7')
