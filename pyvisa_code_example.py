# https://edadocs.software.keysight.com/kkbopen/use-a-python-program-to-output-several-voltage-levels-from-the-e36xxa-series-of-dc-power-supplies-620693041.html
import pyvisa
import pymeasure
print(pymeasure.__file__)

#user define list voltage output
voltages = [0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0]
#Open Connection Keysight Visa 
rm = pyvisa.ResourceManager()
rm.list_resources()
#Connect to VISA Address
#GPIB Connection: 'GPIP0::xx::INSTR'
myinst = rm.open_resource("GPIB0::13::INSTR")
#Set Timeout - 5 seconds
myinst.timeout = 5000
#*IDN? - Query Instrumnet ID    
myinst.write("*IDN?")
#Select Channel Output to program, This line is multiple channel output
myinst.write(':INSTrument:NSELect 1')
#Enable output ON
myinst.write(':OUTPut:STATe 1')
#generate voltage level output in sequence
for i in range(len(voltages)):
    myinst.write(f':SOURce:VOLTage:LEVel:IMMediate:AMPLitude {voltages[i]}')
    #change this delay to increase or decrease output intervals        
    myinst.timeout = 1000
    
myinst.close()
