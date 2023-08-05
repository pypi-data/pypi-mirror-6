

Introduction
============
This Python package contains a mix-mash of tools to assist 
MyHDL designs.  Includes common components and scripts that 
are frequently used in complex digital designs.  The tools
assist in automating FPGA toolflows, simulations, and 
cosimulation.


Simplified FPGA Vendor Tool Flow
=================================
In this package there is an object that represents an FPGA 
development board.  Once a set of boards are defined mapping
a design to the board is straightforward.  Example, given
a simple design that maps one IO to another IO:

::

    def m_map_io(chan):
        @always(chan)
	def assign():
	    chan.next[0] = chan[1]
        return assign

To execute the tool flow, which includes matching the module
ports to the defined ports, synthesize, map, and place-n-route
the design:

::

    brd = get_xilinx_board('xula', top=m_map_io)
    brd.run()    
    
The above couple of lines of code will create the required 
constraint files based on the board definitions and the ports
used in the top-level modules and will run the FPGA tools.  If
the tools execute successfully a bit file will exist and ready
to load into an FPGA.  If the top-level port names do not match
the FPGA pin names (as defined in the board definitions) the 
port to pin mappings will need to be defined manually:

::

    brd = get_xilinx_board('xula')
    brd.set_top(m_button_led)
    brd.add_port('button', Signal(bool(0)), pins=(33,))
    brd.add_port('led', Signal(bool(0)), pins=(32,))
    brd.run()   # run the FPGA vendor tools


Xilinx Boards Defined
----------------------

 * Xess Corp Xula and Xula2
 * Digilent Nexys and Atlys
 * UFO-400
 * DSPtroncis SX1


Altera Boards Defined
---------------------

 * TBC DE2

Lattice Boards Defined
-----------------------

 * TBC


Clock
-----
Typically in a MyHDL design a clock is defined as:

::

    clock = Signal(bool(0))


This package adds an object, *Clock* that is a small wrapper 
with the frequency attribute.  Also a method to generate the 
clock.

::

    clock = Clock(0, frequency=100e6)
    tb_clk = clock.gen()   


It is common for the frequency to be passed to different 
modules as a parameter.  This provides a more convenient 
and easier to maintain option.

The clock generator /gen()/ will try and automatically define
the number of simulation ticks required.  It will always use
a half period simulation tick of three for the fastest clock.
Note, at this point in time this is very primitive, and has 
limited uses for automatic delay generations.  If a lot of 
clock frequencies are used the user will need to set the 
half period ticks

::

   tb_clk = clock.gen(hticks=7)


Reset
-----
This object provides functions to pulse the reset.

::

    reset = Reset(0, active=0, async=True)
    @instance
    def tb_stimulus():
        yield reset.pulse(100)

   #  yield reset.pulse(10)
   #  0  (10)
   #  \_________/e
   #
   #  yield reset.pulse(10,10)
   #  0  (10)     (10)
   #  \________/---------e
   #
   #  yield reset.pulse(10,10,10)
   #  0  (10)       (10)       (10)
   #  ----------\__________/----------e



SignalQueue
-----------
This is useful when interfacing to imperative code.  That is
interfacing to what most would consider typical software.  The
software can push values to the SignalQueue.  When the SignalQueue
has a value it will Signal the RTL.  Provides a bridge from a 
threaded test environment to the MyHDL simulator.

