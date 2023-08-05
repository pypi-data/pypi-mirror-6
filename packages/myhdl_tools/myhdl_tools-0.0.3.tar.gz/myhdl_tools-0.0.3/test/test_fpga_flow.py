
import os
import shutil
from glob import glob

import pytest

from myhdl import *
from myhdl_tools import Clock,Reset
from myhdl_tools.boards import get_xilinx_board

def m_blink(clock,reset,toggle):
    MAX_CNT = int(clock.frequency)
    cnt = Signal(intbv(0,min=0,max=MAX_CNT))
    @always_seq(clock.posedge,reset=reset)
    def hdl():
        if cnt == MAX_CNT-1:
            cnt.next = 0
            toggle.next = not toggle
        else:
            cnt.next = cnt + 1
    return hdl

@pytest.fixture
def clean():
    if os.path.isdir('xilinx/'):
        shutil.rmtree('xilinx/')
    if os.path.isdir('altera/'):
        shutil.rmtree('altera/')
    vlist = glob("*.v*")
    for ff in vlist:
        os.remove(ff)


def test_atlys_vhdl(clean):
    brd = get_xilinx_board('atlys', top=m_blink)
    brd.add_port('toggle', Signal(bool(0)), pins=('U18',)) 
    brd.add_port('reset', Reset(0,active=0,async=True), pins=('T15',))
    brd.run('vhdl')

def test_atlys_vhdl_noclean():
    test_atlys_vhdl(None)

def test_atlys_verilog(clean):
    brd = get_xilinx_board('atlys', top=m_blink)
    brd.add_port('toggle', Signal(bool(0)), pins=('U18',)) 
    brd.add_port('reset', Reset(0,active=0,async=True), pins=('T15',))
    brd.run('verilog')

def test_atlys_verilog_noclean():
    test_atlys_verilog(None)

def test_xula_vhdl(clean):
    brd = get_xilinx_board('xula', top=m_blink)
    brd.add_port('toggle', Signal(bool(0)), pins=(36,)) # not a default pin
    brd.add_port('reset', Reset(0,active=0,async=True), pins=(39,))
    brd.run('vhdl')

def test_xula_verilog(clean):
    brd = get_xilinx_board('xula', top=m_blink)
    brd.add_port('toggle', Signal(bool(0)), pins=(36,)) # not a default pin
    brd.add_port('reset', Reset(0,active=0,async=True), pins=(39,))
    brd.run('verilog')


if __name__ == '__main__':
    tl = (test_xula_vhdl, test_xula_verilog, 
          test_atlys_vhdl, test_atlys_verilog,
          test_xula_vhdl, test_xula_verilog, 
          test_atlys_vhdl, test_atlys_verilog)

    for tt in tl:
        print("*"*68)
        print("*"*68)
        clean()
        tt(None)
        print("*"*68)

    #clean()
    #test_xula_vhdl(None)
    #clean()
    #test_xula_verilog(None)
    #
    #clean()
    #test_atlys_vhdl(None)
    #clean()
    #test_atlys_verilog(None)
