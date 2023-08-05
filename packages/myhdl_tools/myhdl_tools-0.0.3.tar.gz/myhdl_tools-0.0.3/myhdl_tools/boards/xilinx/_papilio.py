#
# Copyright (c) 2013 Alexander Hungenberg
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
from myhdl import Signal, intbv
from ... import Clock
from ..._xilinx import XilinxFPGA

VCCO = 'LVCMOS33'

pone = XilinxFPGA('pone')
pone.set_device('spartan3E', 'xc3s500e', 'VQ100', '-4')
pone.add_port('clock', Clock(0, frequency=32e6), 89, iostandard='LVCMOS25')
pone.add_port('rx', Signal(False), 88, iostandard='LVCMOS33')
pone.add_port('tx', Signal(False), 90, iostandard='LVCMOS33', drive='4', slew='SLOW')

pone.add_port('wingA', Signal(intbv(0)[16:]),
              (18, 23, 26, 33, 35, 40, 53, 57, 60, 62,
               65, 67, 70, 79, 84, 86),
              iostandard=VCCO)
pone.add_port('wingB', Signal(intbv(0)[16:]),
              (85, 83, 78, 71, 68, 66, 63, 61, 58, 54,
               41, 36, 34, 32, 25, 22),
              iostandard=VCCO)
pone.add_port('wingC', Signal(intbv(0)[16:]),
              (91, 92, 94, 95, 98, 2, 3, 4, 5, 9,
               10, 11, 12, 15, 16, 17),
              iostandard=VCCO)

pone.add_port('jtag_tms', Signal(False), 75, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('jtag_tck', Signal(False), 77, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('jtag_tdi', Signal(False), 100, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('jtag_tdo', Signal(False), 76, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('flash_cs', Signal(False), 24, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('flash_ck', Signal(False), 50, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('flash_si', Signal(False), 27, iostandard='LVTTL', drive='8', slew='fast')
pone.add_port('flash_so', Signal(False), 44, iostandard='LVTTL', drive='8', slew='fast', pullup=True)