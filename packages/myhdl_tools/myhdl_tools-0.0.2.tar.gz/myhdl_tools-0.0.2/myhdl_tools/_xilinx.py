#!/usr/bin/env python
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
 
import sys
import os
from time import gmtime, strftime
import subprocess
import shutil
from pprint import pprint

from _fpga import _fpga

from _mysigs import Clock,Reset

_xilinx_default_pin_attr = {
    "NET": None,
    "LOC" : None,
    "IOSTANDARD": None,
    "SLEW": None,
    "DRIVE": None
    }
 
class _ise(object):
    """ """
    
    def __init__(self, top_name=None, path=None):
        self._path = path if path is not None else '.'
            
        self._fpga = None
        self.tcl_name = None
        self.top_name = None
        self.hdl_files = None
        self.hdl_file_list = []
        
        if top_name:
            if isinstance(top_name, str):
                self.top_name = top_name
                self.tcl_name = top_name + '.tcl'
            else:
                raise TypeError('top_name needs to be string')
 
        # start with the text string for the TCL script
        self.tcl_script = '#\n#\n# ISE implementation script\n'
        date_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        self.tcl_script += '# create: %s\n' % \
                           date_time
        self.tcl_script += '# by: %s\n' % \
                           os.path.basename(sys.argv[0])
        self.tcl_script += '#\n#\n'

    def add_files(self, fn):
        if isinstance(fn, (list,tuple)):
            for ff in fn:
                if not isinstance(ff,str):
                    raise TYpeError("list or tuple entry needs ot be a string")
                self.hdl_file_list.append(ff)
        elif isinstance(files,str):
            self.hdl_file_list.append(files)
        
    def create_tcl(self, filename=None):
        """Create the project TCL script
        """
        print(self._path,filename,self.tcl_name)
        if filename:
            fn = os.path.join(self._path, filename)
        else:
            fn = os.path.join(self._path, self.tcl_name)
 
        self.tcl_script += '# set compile directory:\n'
        #self.tcl_script += 'set compile_directory %s\n'%self._path
        self.tcl_script += 'set compile_directory %s\n'%'.'

        if self.top_name:
            self.tcl_script += 'set top_name %s\n'%self.top_name
            self.tcl_script += 'set top %s\n'%self.top_name

        # @todo: add one file at a time, explicit
        #-#if self.hdl_files:
        #-#    self.tcl_script += '# input source files:\n'
        #-#    self.tcl_script += 'set hdl_files [ list \\\n'
        #-#    for f in self.hdl_file_list:
        #-#        self.tcl_script += ' '*17
        #-#        self.tcl_script += '%s \\\n'%f
        #-#        self.tcl_script += ']\n'
 
 
        self.tcl_script += '# set Project:\n'
        self.tcl_script += 'set proj %s\n'% self.top_name
 
        # @note: because the directory is changed everything
        #        is relative to self._path
        self.tcl_script += '# change to the directory:\n'
        self.tcl_script += 'cd %s\n'% self._path
 
        # @todo: verify UCF file exists
        bdir,ucffn = os.path.split(self.fpga.ucf_file)
        self.tcl_script += '# set ucf file:\n'
        self.tcl_script += 'set constraints_file %s\n'% (ucffn)

        #-## test whether ise project file exits
        #-## @todo: check the Xilinx version, if greater than ??? use xise
        #-##        else use .ise
        #-#f = os.path.join(self._path, self.top_name + '.xise')
        #-#if os.path.exists(f):
        #-#    os.remove(f)

        self.tcl_script += '# set variables:\n'
        pj_fn = self.top_name + '.xise'
        # Create or open an ISE project (xise?)
        print('Project name : %s ' % (pj_fn))
        pjfull = os.path.join(self._path,pj_fn)
        if os.path.isfile(pjfull):
            self.tcl_script += 'project open %s \n' % (pj_fn)
        else:
            self.tcl_script += 'project new %s\n' % (pj_fn)
    
        if self.fpga.family:
            self.tcl_script += 'project set family %s\n'%self.fpga.family
            self.tcl_script += 'project set device %s\n'%self.fpga.device
            self.tcl_script += 'project set package %s\n'%self.fpga.package
            self.tcl_script += 'project set speed %s\n'%self.fpga.speed
 
        # add the hdl files
        self.tcl_script += '\n'
        self.tcl_script += '# add hdl files:\n'
        #self.tcl_script += 'xfile add %s\n'%(ucffn)
        for hdl_file in self.hdl_file_list:
            self.tcl_script += 'xfile add %s\n'%hdl_file
 
        self.tcl_script += '# test if set_source_directory is set:\n'
        self.tcl_script += 'if { ! [catch {set source_directory'
        self.tcl_script += ' $source_directory}]} {\n'
        self.tcl_script += '  project set "Macro Search Path"\n'
        self.tcl_script += ' $source_directory -process Translate\n'
        self.tcl_script += '}\n'
 
        # @todo : need an elgent way to manage all the insane options, 90% 
        #         of the time the defaults are ok, need a config file or 
        #         something to overwrite.  These should be in a dict or
        #         refactored or something
        self.tcl_script += "project set \"FPGA Start-Up Clock\" \"JTAG Clock\" -process \"Generate Programming File\" \n"

        # run the implementation
        self.tcl_script += '# run the implementation:\n'
        self.tcl_script += 'process run "Synthesize" \n'
        self.tcl_script += 'process run "Translate" \n'
        self.tcl_script += 'process run "Map" \n'
        self.tcl_script += 'process run "Place & Route" \n'
        self.tcl_script += 'process run "Generate Programming File" \n'
        # close the project
        self.tcl_script += '# close the project:\n'
        self.tcl_script += 'project close\n' 
 
        fid = open(fn, 'w')
        fid.write(self.tcl_script)
        fid.close() 
 
    def run(self, filename=None):
        """Run the created TCL script """
        if filename:
            tcl_name = filename
        else:
            tcl_name = os.path.join(self._path, self.tcl_name)
 
        if not os.path.exists(self._path):
            os.mkdir(self._path)
 
        cmd = ['xtclsh', tcl_name]
        print('running command: %s'%(cmd))
        try:
            txt = subprocess.check_call(cmd,
                                        stderr=subprocess.STDOUT)
        except Exception, err:
            print(err)

    @property
    def fpga(self):
        return self._fpga
    @fpga.setter
    def fpga(self, fpga):      
        self._fpga = fpga

  
class XilinxFPGA(_fpga):
    def __init__(self, prj_name='', path=None):
        self._path = path if path is not None else '.'
        
        self.ucf_file = None
        self.family = None
        self.device = None
        self.package = None
        self.speed = None
        _fpga.__init__(self)
        self.top_name = prj_name

        # @todo: verify this is the correct intended usage, i.e. 
        #        the file list doesn't already exist somewhere
        self.hdl_file_list = []
                                      
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self,p):
        self._path = p
        
    def set_device(self, family, device, package, speed):
        
        if not isinstance(family, str):
            raise TypeError('"Family" needs to be a string')
        if not isinstance(device, str):
            raise TypeError('"Device" needs to be a string')
        if not isinstance(speed, str):
            raise TypeError('"Speed" needs to be a string')
        if not isinstance(package, str):
            raise TypeError('"Package" needs to be a string')
      
        self.family = family
        self.device = device
        self.package = package
        self.speed = speed
            
      
    def create_ucf(self, filename='my.ucf'):
        self.ucf_file = os.path.join(self._path, filename)
        ustr = ""
        #ustr = '# UCF file automatically create by "%s"\n'% \
        #       os.path.basename(sys.argv[0])

        print(type(self.ports),self.ports)
        ustr += "#\n"
        for port_name,port in self.ports.items():
            if port.inuse:
                _pins = port.pins

                for ii,pn in enumerate(_pins):
                    if len(_pins) == 1:
                        ustr += "NET \"%s\" " % (port_name)
                    else:
                        ustr += "NET \"%s<%d>\" " % (port_name,ii)

                    # pure numeric pins need a preceeding "p" otherwise
                    # use the string defined
                    if isinstance(pn,str):
                        ustr += "LOC = \"%s\" " % (str(pn))
                    else:
                        ustr += "LOC = \"p%s\" " % (str(pn))

                    # additional pin parameters
                    for kp,vp in port.kwargs.items():
                        if kp.lower() in ("pullup",) and vp is True:
                            ustr += " | %s " % (kp)
                        else:
                            ustr += " | %s = %s " % (kp,vp)
                    ustr += ";\n"
                
        ustr += "#\n"

        # @todo: loop through the pins again looking for clocks
        for port_name,port in self.ports.items():
            if port.inuse and isinstance(port.sig,Clock):
                period = 1/(port.sig.frequency/1e9)
                ustr += "NET \"%s\" TNM_NET = \"%s\"; \n" % (port_name,port_name)
                ustr += "TIMESPEC \"TS_%s\" = PERIOD \"%s\" %.7f ns HIGH 50%%;" \
                    % (port_name,port_name,period)
                ustr += "\n"
        ustr += "#\n"

        fid = open(self.ucf_file, 'w')
        fid.write(ustr)
        fid.close()      
        print(ustr)

    def run(self, use='verilog'):
        self.convert(to=use)
        self.create_ucf(filename=self.name+'.ucf')
        self._tool_chain = _ise(top_name=self.top_name,path=self._path)
        self._tool_chain.fpga = self
        pprint(vars(self._tool_chain.fpga))

        # @todo: verify the following is correct, that is the filename
        #        doesnt' already exist some where.
        self.hdl_file_list.append(self.top_name+'.v')
        self._tool_chain.add_files(self.hdl_file_list)

        # create the TCL file and run the tools
        self._tool_chain.create_tcl()
        self._tool_chain.run()
        
    def __repr__(self):
        s = 'FPGA:\n'
        if self.family:
          s += 'Family: %s\n'% self.family
        s += 'Device: %s\n'% self.device
        s += 'Package: %s\n'% self.package
        s += 'Speed: %s\n'% self.speed
        return s
 
