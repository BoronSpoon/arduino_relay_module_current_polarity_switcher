from pymeasure.instruments.electricalsource import E3646A
from pymeasure.instruments.opticalmeter import YokogawaAD6370D
rm = pyvisa.ResourceManager()
print(rm.list_resources())
sa = YokogawaAD6370D(gpibAddress=8) 
relay_ser = serial.Serial('COM3', 9600, timeout=0)
DC = E3646A(resourceName = "GPIB0::16::INSTR")
import pyvisa
import serial
from time import sleep
import numpy as np 
import datetime
from matplotlib import pyplot as plt

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
    sa.center = 1552
    sa.span = 1
    sa.sweep_average = 1
    sa.point_average = 1
    sa.resolution = 0.05

def setup():
    setSpeana()
    global relay_ser, DC, measured_voltages, measured_resonant_wavelengths
    measured_voltages = []
    measured_resonant_wavelengths = []
    DC.initialize()
    DC.ch(1)
    DC.volt(0)
    DC.on()
    
def finalize():
    global relay_ser, DC, measured_voltages, measured_resonant_wavelengths
    relay_ser.close()
    DC.off()
    DC.finalize()

def set_voltage(voltage, timeout=0.01, relay_timeout=0.1):
    global relay_ser, DC, measured_voltages, measured_resonant_wavelengths
    if voltage >= 0:
        relay_ser.write(b'p') # positive polarity
        print("setting polarity into positive", end= ": ")
        sleep(relay_timeout)
    else:
        relay_ser.write(b'n') # negative polarity
        print("setting polarity into negative", end= ": ")
        sleep(relay_timeout)
    DC.volt(abs(voltage))
    sleep(timeout)
    DC.volt(0)

def get_hysterisis(max=8): # 8V is max in low:P8V range (8V 726mA 150 Oe at 1cm distance)
    global relay_ser, DC, measured_voltages, measured_resonant_wavelengths
    # neg2pos goes up from -max to +max
    for direction in ["neg2pos", "pos2neg"]:
        if direction == "neg2pos":
            voltages = np.linspace(-max,max,20)
        elif direction == "pos2neg":
            voltages = np.linspace(max,-max,20)
        for voltage in voltages:
            if direction == "neg2pos":
                DC.set_voltage(1*max, timeout=0.01) # saturate in the opposite polarity
            elif direction == "pos2neg":
                DC.set_voltage(-1*max, timeout=0.01) # saturate in the opposite polarity    
            DC.set_voltage(voltage, timeout=0.01)
            DC.set_voltage(0, timeout=0.01) # measure remanance
            ##################################################################
            ######## measure and calculate resonance wavelength here #########
            ##################################################################        
            sa.sweep()
            global i 
            wavelength = sa.getXValue(unit=NANO_METER)
            transmittance = sa.getYValue(unit=DBM)
            resonant_wavelength = wavelength[np.argmin(transmittance)]
            measured_voltages.append(voltage)
            measured_resonant_wavelengths.append(resonant_wavelength)

    ##################################################################
    ######## plot and save here #########
    ##################################################################        
    plt.plot(measured_voltages, measured_resonant_wavelengths)
    plt.xlabel("voltage (V)")
    plt.xlabel("resonant wavelength (nm)")
    plt.savefig("hysterisis_"+datetime.datetime.now()+".png")
    plt.show()

if __name__ == "__main__":
    setup()
    get_hysterisis()
    finalize()