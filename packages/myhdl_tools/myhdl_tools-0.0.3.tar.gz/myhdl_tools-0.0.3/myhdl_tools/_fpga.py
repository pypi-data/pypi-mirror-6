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
import shutil
import inspect
from pprint import pprint
from random import randint
from copy import copy

import myhdl

from _mysigs import Clock

                
class _port(object):
    """ Generic pin/port definitions """
    
    def __init__(self, name, sig, pins, **kwargs):
        # add all the default attributes depeding on
        
        # fpga type
        self.name = name
        self.sig = sig
        self.pins = pins
        self.inuse = False

        # device specific arguments, when the pin assignment
        # list is created the following will be used to create
        # the UCF,TCL,etc input
        self.kwargs = kwargs
        
    def help(self):
        pass #useful help print!

class _fpga(object):

    def __init__(self):
        
        # add the default attributes (parameters)
        self.top = None
        self.tp = None
        self.top_name = None
        # keep track of all the thingies
        self.ports = {}
        self.clocks = {}

    def has_top(self):
        return self.top is not None
    
    def set_top(self, top, **params):
        self.top = top
        self.tp = params

    def pathexist(self, pth):
        """ create the working directory path if needed
        """
        if os.path.isfile(pth):
            pth,fn = os.path.split(pth)
        fpth = ''
        path_split = os.path.split(pth)
        for ppth in pth.split(os.path.sep):
            fpth = os.path.join(fpth,ppth)
            if not os.path.isdir(fpth):
                print("path create %s"%(fpth))
                os.mkdir(fpth)

        return os.path.isdir(pth)

    def _get_name(self, name=None):
        if name is None:
            if self.top_name is not None:
                name = self.top_name
            else:
                name = self.top.func_name

        return name

    def _scrub(self, filelist):
        """
        remove the generated files from the file list, if the
        toolflow is run subsequent times the converted files 
        are added each time (especially bad when running one
        conversion type and then the other)
        """
        print(filelist)
        name = self._get_name()
        fl = copy(filelist)
        for ii,ff in enumerate(fl):
            print(" ... %s"%(ff))
            if (ff == "%s.v"%(name) or 
                ff == "%s.vhd"%(name)):
                print("scrubbing %s"%(ff))
                filelist.remove(ff)
            elif "pck_myhdl" in ff:
                print("scrubbing %s"%(ff))
                filelist.remove(ff)

    def convert(self, name=None, to='verilog', **kwargs):
        """ convert the myhdl design to Verilog or VHDL and copy to working dir
        """
        assert to in ('verilog', 'vhdl'), \
               "Incorrect conversion type: %s" % (self.conversion_type)

        name = self._get_name(name)

        # get the top-level ports and parameters.
        pp = inspect.getargspec(self.top) # pp = portsparams

        # all of the arguments (no default values) are treated as
        # ports.  This doesn't mean it needs to be a port but it
        # is convention that ports are the arguments and parameters
        # are keyword arguments.  A parameter can exist in this
        # list but it can't be empty in conversion
        hdlports = {}
        if pp.defaults is not None:
            pi = len(pp.args)-len(pp.defaults)
        else:
            pi = len(pp.args)
        for pn in pp.args[:pi]:
            hdlports[pn] = None
        params = {}
        for ii,kw in enumerate(pp.args[pi:]):
            params[kw] = pp.defaults[ii]

        # see if any of the ports or parameters have been overridden
        if self.tp is not None:
            for k,v in self.tp.items():
                if hdlports.has_key(k):
                    hdlports[k] = v
            for k,v in self.tp.items():
                if params.has_key(k):
                    params[k] = v
                
        for k,v in kwargs.items():
            if hdlports.has_key(k):
                hdlports[k] = v
        for k,v in kwargs.items():
            if params.has_key(k):
                params[k] = v
        print('HDL PORTS:  ',hdlports)
        print('HDL PARAMS: ',params)
        
        # match the fpga ports to the hdl ports, not if a port is
        # a keyword argument in the top-level this will fail
        for port_name,port in self.ports.items():
            if hdlports.has_key(port_name):
                hdlports[port_name] = port.sig
                port.inuse = True

        for k,v in hdlports.items():
            assert v is not None, "Error unspecified port %s"%(k)
            
        # combine the ports and params
        pp = hdlports.copy()
        pp.update(params)
        
        # convert with the ports and parameters        
        if to.lower() == 'verilog':
            if name is not None:
                myhdl.toVerilog.name = name
            myhdl.toVerilog(self.top, **pp)
            self.name = name
            self.vfn = "%s.v"%(name)
        elif to.lower() == 'vhdl':
            if name is not None:
                myhdl.toVHDL.name = name
            myhdl.toVHDL(self.top, **pp)
            self.name = name
            self.vfn = "%s.vhd"%(name)
        else:
            raise ValueError("Incorrect conversion target %s"%(to))

        # make sure the working directory exists
        assert self.pathexist(self._path)

        # copy files etc to the working directory
        tbfn = 'tb_'+self.vfn
        ver = myhdl.__version__
        # remove special characters from the version
        for sp in ('.', '-', 'dev'):
            ver = ver.replace(sp,'')
        pckfn = 'pck_myhdl_%s.vhd'%(ver)
        for src in (self.vfn,tbfn,pckfn):
            dst = os.path.join(self._path,src)
            print('   checking %s'%(dst))
            if os.path.isfile(dst):
                print('   removing %s'%(dst))
                os.remove(dst)
            if os.path.isfile(src):
                print('   moving %s --> %s'%(src,self._path))
                shutil.move(src,self._path)

        if to.lower() == 'verilog':
            filelist = (self.vfn,)
        elif to.lower() == 'vhdl':
            filelist = (self.vfn, pckfn,)

        return filelist

    def add_port(self, name, sig, pins, **kwargs):
        if isinstance(pins, (str, int)):
            pins = (pins,)
        assert isinstance(pins, (list,tuple)), \
            "pins must be a list/tuple of pins (or a single str/int)"
        self.ports[name] =  _port(name, sig, pins, **kwargs)
        if isinstance(sig, Clock):
            self.clocks[name] = self.ports[name]

    def name_port(self, name, port, slice_=None, **kwargs):
        """Extract "slices" from a port
        Makes it possible to extract and name a single port (a range 
        of ports) out of a larger port array. This could be useful to 
        give meaningful names to single ports e.g. on Papilio Wings.

        Example: board.name_port('led', 'wingC', 7)
        where wingC is a 16-bit port array.

        To extract a port range the slice class has to be used. E.g.
        board.name_port('MSB', 'wingC', slice(16,8))"""

        p = self.ports[port]
        if slice_ is None:
            pins = p.pins
            sig = p.sig
        else:
            assert isinstance(slice_, (slice, int)), "slice_ has to be either None or a int/slice object"
            pins = p.pins[slice_]
            sig = myhdl.Signal(p.sig[slice_])
        kws = p.kwargs.copy()
        kws.update(kwargs)
        self.add_port(name, sig, pins, **kws)
            
    def run(self):
        pass
