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


# Nexsys
nexys = XilinxFPGA('nexys')
nexys.add_port('clock', Clock(0, frequency=50e6), pins=('A8',))
nexys.add_port('reset', Reset(0,active=0,async=True), pins=(13,))

nexys.add_port('led', Signal(intbv(0)[8:]), 
               pins=('R16','P14','M13','N14',
                     'L12','M14','L13','L14',))
nexys.add_port('btn', Signal(intbv(0)[4:]),
               pins=('K12','K13','K14','J13',))
nexys.add_port('sw', Signal(intbv(0)[8:]),
               pins=('N16','M15','M16','L15',
                     'K15','K16','J16','N15',))


# set the FPGA device on the board
nexys.set_device('spartan3e', 'XC3S500E', 'vq100', '-5')
