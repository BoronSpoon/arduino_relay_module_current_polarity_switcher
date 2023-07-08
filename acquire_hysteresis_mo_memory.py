from pymeasure.instruments.electricalsource import E3646A
from pymeasure.instruments.opticalmeter import YokogawaAD6370D
from pymeasure.units.SI import NANO,METER,DECIBEL,HELTZ,NANO_METER
from pymeasure.units.other.power import DBM
import pyvisa
import serial
rm = pyvisa.ResourceManager()
print(rm.list_resources())
sa = YokogawaAD6370D(gpibAddress=8) 
DC = E3646A(resourceName = "GPIB0::16::INSTR")
import serial
from time import sleep
import numpy as np 
import datetime
from matplotlib import pyplot as plt
import os
import scipy.io
cwd = os.path.dirname(__file__)

#with serial.Serial('COM6', 115200, write_timeout=0, timeout=0) as relay_ser:
#sleep(2)
plot_params = {
    "axes.labelsize": 16,
    "axes.titlesize": 16,    
    "lines.linestyle": "solid",
    "lines.linewidth": 1,
    "lines.marker": "o",
    "lines.markersize": 3,
    "xtick.major.size": 3.5,
    "xtick.minor.size": 2,
    "xtick.labelsize": 13,
    "ytick.major.size": 3.5,
    "ytick.minor.size": 2,
    "ytick.labelsize": 13,
}
plt.rcParams.update(plot_params)
    
#スペアナの測定条件    
def setSpeana():
    sa.center = 1542
    sa.span = 5
    sa.sweep_average = 1
    sa.point_average = 1
    sa.resolution = 0.05

def setup():
    setSpeana()
    global measured_voltages, measured_resonant_wavelengths
    measured_voltages = []
    measured_resonant_wavelengths = []
    DC.initialize()
    DC.ch(1)
    DC.volt(0)
    DC.on()
    
def finalize():
    global measured_voltages, measured_resonant_wavelengths
    #relay_ser.close()
    DC.off()
    DC.finalize()

def set_voltage(voltage, timeout=0.01, relay_timeout=0.5):
    global measured_voltages, measured_resonant_wavelengths
    if voltage > 0:
        DC.ch(2)
        DC.volt(5)
        DC.ch(1)
        """
        relay_ser.write(b'p') # positive polarity
        print("p")
        while(True):
            if relay_ser.read() == b"p":
                print("read p")
                relay_ser.read(size=100) # flush read buffer
                break
        #print("setting polarity into positive", end= ": ")
        """
    elif voltage < 0:
        DC.ch(2)
        DC.volt(0)
        DC.ch(1)
        """
        relay_ser.write(b'n') # negative polarity
        print("n")
        while(True):
            if relay_ser.read() == b"n":
                print("read n")
                relay_ser.read(size=100) # flush read buffer
                break
        #print("setting polarity into negative", end= ": ")
        """
    DC.volt(abs(voltage))
    sleep(timeout)
    DC.volt(0)

def get_hysterisis(max_=0.1, timeout=0.1, points=21): # 8V is max in low:P8V range (8V 726mA 150 Oe at 1cm distance)
    global measured_voltages, measured_resonant_wavelengths
    measured_voltages = []
    measured_resonant_wavelengths = []
    data = []
    # neg2pos goes up from -max to +max
    for direction in ["neg2pos", "pos2neg"]:
        if direction == "neg2pos":
            voltages = np.linspace(-1*max_,max_,points)
        elif direction == "pos2neg":
            voltages = np.linspace(max_,-1*max_,points)
        for voltage in voltages:
            #print(voltage)
            if direction == "neg2pos":
                #print("a,"+str(1*max_))
                set_voltage(1*max_, timeout=timeout) # saturate in the opposite polarity
            elif direction == "pos2neg":
                #print("a,"+str(-1*max_))
                set_voltage(-1*max_, timeout=timeout) # saturate in the opposite polarity    
            set_voltage(voltage, timeout=timeout)
            #set_voltage(0, timeout=timeout) # measure remanance
            ##################################################################
            ######## measure and calculate resonance wavelength here #########
            ##################################################################        
            
            sa.sweep()
            global i 
            wavelength = sa.getXValue(unit=NANO_METER)
            transmittance = sa.getYValue(unit=DBM)
            if len(data) == 0: # first row is wavelength
                data.append(wavelength)
            data.append(transmittance) # 2nd ~ last row is transmittance at each voltages
            resonant_wavelength = wavelength[np.argmin(transmittance)]
            measured_voltages.append(voltage)
            measured_resonant_wavelengths.append(resonant_wavelength)
            

    ##################################################################
    ######## plot and save here #########
    ##################################################################        
    
    plt.tight_layout()
    plt.figure(1)
    plt.plot(measured_voltages, measured_resonant_wavelengths)
    plt.xlabel("voltage (V)")
    plt.ylabel("resonant wavelength (nm)")
    plt.savefig(os.path.join(cwd, "results", "hysterisis_"+str(datetime.datetime.now()).replace(" ", "").replace("-", "_").replace(":", "_").replace(".", "_")+".png"), bbox_inches="tight")
    plt.figure(2)
    data = np.transpose(np.array(data))
    for i in range(data.shape[1]-1):
        plt.plot(data[:,0], data[:,i+1], label=str(measured_voltages[i]))
    plt.xlabel("wavelength (nm)")
    plt.ylabel("transmittance (dBm)")
    plt.legend(title="applied voltage (V)")
    plt.savefig(os.path.join(cwd, "results", "transmittance_"+str(datetime.datetime.now()).replace(" ", "").replace("-", "_").replace(":", "_").replace(".", "_")+".png"), bbox_inches="tight")
    # save 
    scipy.io.savemat(
        os.path.join(
            cwd, 
            "results", 
            "data_"+str(datetime.datetime.now()).replace(" ", "").replace("-", "_").replace(":", "_").replace(".", "_")+".mat"
        ), {
            "voltage(V)": np.array(measured_voltages),
            "field(Oe)": 150*np.array(measured_voltages)/8,
            "data": data,
        }
    )
    plt.show()
    

if __name__ == "__main__":
    setup()
    get_hysterisis(max_=8, points=9) # 8V amplitude
    finalize()