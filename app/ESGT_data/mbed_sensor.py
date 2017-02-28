# Author: Kairi Kozuma Boa-Lin Lai
# Python: 2.7.9
# Date  : 02/01/2017

# Libraries needed

# Attempt import of RPi, show warning if exception occurs (for testing on non Raspberry Pi)
try:
    import RPi.GPIO as GPIO
except RuntimeError, e:
  print('Not on a Raspberry Pi: ' + str(e))

import time
import serial
from sensor import Sensor
#function w/ # data pts to read and at what frequency (reads per sec?)
# private var for chaning time interval

# Mbed serial device

class MbedSensor(object):
    COMM_GET_HEADER = '0' # tell mbed to send headers
    COMM_GET_VALUE = '1' # tell mbed to send sensor values
    COMM_INVALID_HEADER = 'DISCONNECTED'
    def __init__(self):
        self.ser = None
        try:# Serial connection to mbed (virtual COM through USB)
            self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.2)
            if(self.ser.isOpen()): self.ser.close()
            self.ser.open()
        except serial.serialutil.SerialException:
             print("Error connecting to mbed")
        # Use BCM pin numbers, instead of Raspberry pin numbers
        GPIO.setmode(GPIO.BCM)
        # Functions to read analog data from mbed
        # Get header values (names of sensors)
        self.number_of_sensors = 0
        self.parse_header(self.mbed_read_header())
        timeout = time.time() + 5 # 5 seconds from now
        while True:
            if len(self.header_list) == 6 or time.time() > timeout:
                break
            self.parse_header(self.mbed_read_header())
        print(self.header_list)
        time.sleep(.5)
    def mbed_read_header(self):
        self.ser.write(MbedSensor.COMM_GET_HEADER)
        time.sleep(.20)
        return self.ser.readline()
     # Get sensor values (0.0 to 1.0)
    def mbed_read_sensors(self):
        self.ser.write(MbedSensor.COMM_GET_VALUE)
        time.sleep(.20)
        return self.ser.readline() # PROBLEM: Need a try() statement, b/c doesn't wait for clear channel
    # Parser for header
    def parse_header(self,raw_header_string):
        raw_header_string = raw_header_string.replace(' ','')
        self.header_list = raw_header_string.split(',')
        self.number_of_sensors = len(self.header_list)
        #return header_list

    # Parser for sensor values
    def parse_sensor_values(self, raw_sensor_string):
        sensor_list_string = raw_sensor_string.replace(' ','').split(',')
        sensor_list = [-1.0] * self.number_of_sensors
        for i in range(len(sensor_list)):
            sensor_list[i] = float(sensor_list_string[i])
            if (self.header_list[i] == MbedSensor.COMM_INVALID_HEADER):
                sensor_list[i] = -1
            else:
                sensor_list[i] = float(sensor_list_string[i])
        return sensor_list


    """
      Define sensors featuers on the followig part.. init once, change the value upon request
    """
    def light_lamda_func(self, x):
        return x+x
    '''
      For Jonathan: def more sensor function
    '''
    def get_json(self):
        value_list = self.parse_sensor_values(self.mbed_read_sensors())
        print(value_list)
        light_sensor = Sensor('light', '42', 'ESGT', self.light_lamda_func)
        light_sensor.set_value(value_list[0])
        return light_sensor.to_json_string()

