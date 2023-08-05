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

import os
import subprocess
import shutil
import myhdl as _myhdl

class Simulator:
    """
    This class is intended to be used with "testbench" method
    of testing converted MyHDL modules.  The "testbench" method
    refers to a convertible testbench.  The same checks that
    are performed in the python code is performed in V* code.
    """
    
    vhdl_dir = 'vhdl/'
    verilog_dir = 'verilog/'
    build_dir = 'build/'
    
    def __init__(self):
        self.testbench = None
        self.hdl_path = None

    def _get_pck(self):
        ver = _myhdl.__version__
        ver = ver.replace('.', '')[:2]
        pck = "pck_myhdl_%s.vhd" % (ver)
        return pck
    
    def convert(self, testbench):
        self.testbench = testbench

    def compile(self):
        pass

    def run(self):
        pass

    def all(self, testbench):
        self.convert(testbench)
        self.compile()
        self.run()
        

# need a better name??
class Myhdl(Simulator):
    name = 'myhdl'
    def run(self):
        assert self.testbench is not None
        _myhdl.Simulation(self.testbench()).run()
        
class Ghdl(Simulator):
    name = 'ghdl'
    def convert(self, testbench):
        assert testbench is not None
        self.testbench = testbench
        tb = testbench
        
        self.hdl_path = os.path.join(self.vhdl_dir, tb.func_name+'.vhd')
        pck = self._get_pck()
        self.pck_path = os.path.join(self.vhdl_dir, pck)
        if not os.path.isdir(self.vhdl_dir):
            os.mkdir(self.vhdl_dir)
        if os.path.isfile(self.hdl_path):
            os.remove(self.hdl_path)
        _myhdl.toVHDL(tb)
        shutil.move(tb.func_name+'.vhd', self.vhdl_dir)
        if os.path.isfile(self.pck_path):
            os.remove(self.pck_path)
        shutil.move(pck, self.pck_path)
        
    def compile(self):
        assert self.testbench is not None
        pck = self._get_pck()
        subprocess.check_output(['ghdl', '-a', '%s' % (self.pck_path)],
                                stderr=subprocess.STDOUT)
        subprocess.check_output(['ghdl', '-a', '%s' % (self.hdl_path)],
                                stderr=subprocess.STDOUT)
        subprocess.check_output(['ghdl', '-e', '%s' % (self.testbench.func_name)],
                                stderr=subprocess.STDOUT)

    def run(self):
        try:
            stext = subprocess.check_output(['ghdl', '-r',
                                             '%s' % (self.testbench.func_name)],
                                            stderr=subprocess.STDOUT)
        except Exception, err:
            stext = err.output
            if 'End of Simulation' in stext:
                pass # continue all is ok
            else:
                raise err
            
        if 'AssertionError' in stext:
            raise StandardError('VHDL simulation failed')

class Icarus(Simulator):        
    name='icarus'
    def convert(self, testbench):
        assert testbench is not None
        self.testbench = testbench
        tb = testbench
        
        self.hdl_path = os.path.join(self.verilog_dir, tb.func_name+'.v')
        if not os.path.isdir(self.verilog_dir):
            os.mkdir(self.verilog_dir)
        if os.path.isfile(self.hdl_path):
            os.remove(self.hdl_path)
        _myhdl.toVerilog(tb)
        shutil.move(tb.func_name+'.v', self.verilog_dir)

    def compile(self):
        self.out = self.hdl_path[:-2]
        subprocess.check_output(['iverilog',
                                 '-o',
                                 '%s' % (self.out),
                                 '%s' % (self.hdl_path)],
                                stderr=subprocess.STDOUT)
        
    def run(self):
        stext = subprocess.check_output([self.out],
                                        stderr=subprocess.STDOUT)
        if 'AssertionError' in stext:
            raise StandardError('Verilog simulation failed')


AllSims = [Myhdl(), Ghdl(), Icarus()]

def run_all(test):
    for sim in AllSims:
        try:
            test(sim)
            print('   %-8s:%s: success' % (sim.name, test.func_name))
        except Exception, err:
           print('   %-8s:%s: failed %s' % (sim.name, test.func_name, err))

