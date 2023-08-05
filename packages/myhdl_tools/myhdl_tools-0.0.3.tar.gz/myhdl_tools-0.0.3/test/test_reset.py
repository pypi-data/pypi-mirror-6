
from myhdl import *
from myhdl_tools import Clock,Reset

def test_reset():

    def _test():
        clock = Clock(0)
        reset = Reset(1, active=0, async=True)
        
        Pulses = [10, (10,), (10,10), (10,10,10)]
        pcnt = Signal(0)
        rtst = Signal(-1)
        
        tbclk = clock.gen()
        
        @instance
        def tbmon():
            while True:
                yield reset.negedge
                pcnt.next = pcnt + 1
            
        @instance
        def tbstim():
            yield delay(10)
            ts = now()
            for ii,pp in enumerate(Pulses):
                rtst.next = rtst + 1
                yield reset.pulse(pp)
                yield delay(10)
            te = now()
            assert te-ts == 70+10*len(Pulses)
            yield delay(10)
            assert pcnt == 4, "%d"%(pcnt)

            raise StopSimulation

        return tbclk, tbmon, tbstim

    Simulation(_test()).run()

        
if __name__ == '__main__':
    test_reset()
