import serial
import visa
# https://github.com/MarkDing/GPIB-pyvisa
    
def setup():
    global relay_ser, DC
    relay_ser = serial.Serial('COM3', 9600, timeout=0):

    rm = visa.ResourceManager()
    res = rm.list_resources()
    print("Find following resources: ")
    print(res)
    print("Opening " + res[-1])

    DC = rm.open_resource(res[-1])
    DC.query("*IDN?")

def set_voltage(voltage):
    global relay_ser, DC
    if voltage == 0:
        DC.write("OUTP OFF")
    elif voltage > 0:
        relay_ser.write(b'p') # positive polarity
        print("setting polarity into positive", end= ": ")
        s = relay_ser.read(100)
        if s == "polarity set to positive":            
            DC.write("INST P8V") # Select +8V output
            DC.write(f"VOLT {abs(voltage)}") # Set output voltage            
            DC.write("OUTP ON")
            # set DC power source to abs(voltage) V
            print("success")
        elif s == "please provide p or n for changing polarity":
            print("please provide p or n for changing polarity")
    else:
        relay_ser.write(b'n') # negative polarity
        print("setting polarity into negative", end= ": ")
        s = relay_ser.read(100)
        if s == "polarity set to negative":
            DC.write("INST P8V") # Select +8V output
            DC.write(f"VOLT {abs(voltage)}") # Set output voltage            
            DC.write("OUTP ON")
            print("success")
        elif s == "please provide p or n for changing polarity":
            print("please provide p or n for changing polarity")

if __name__ == "__main__":
    setup()
    