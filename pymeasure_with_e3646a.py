from pymeasure.instruments.electricalsource import E3646A
from time import sleep

import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())

DC = E3646A(resourceName = "GPIB0::16::INSTR")
DC.initialize()
DC.ch(1)
DC.off()
for i in [0,0.1,0,0.1,0,0.1,0,0.1,0]:
    DC.off()
    DC.volt(i)
    DC.on()
    DC.meas_cur()
    sleep(1)
DC.finalize()