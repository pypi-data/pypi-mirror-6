
from myhdl import *
from myhdl_tools import Clock

def test_clock():

    def _test():
        clock1 = Clock(0, frequency=50e6)
        clock2 = Clock(0, frequency=100e6)
        clock3 = Clock(1, frequency=12.5e6)

        # the clock module will default to 3 half period
        # ticks (full period 6 sim ticks) need to set the
        # hticks for the different clocks.
        tbclk1 = clock1.gen(hticks=6)
        tbclk2 = clock2.gen(hticks=3)
        tbclk3 = clock3.gen(hticks=24)

        @instance
        def tbstim():
            for cc,ed in zip((clock1,clock2,clock3),(12,6,48)):
                yield cc.posedge
                ts = now()
                yield cc.posedge
                te = now()
                assert te-ts == ed, "%d != %d"%(te-ts,ed)

            raise StopSimulation
            
            
        return tbclk1, tbclk2, tbclk3, tbstim

    Simulation(_test()).run()


if __name__ == '__main__':
    test_clock()
