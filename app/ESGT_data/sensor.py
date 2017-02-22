##!/usr/bin/python
'''
File name: ESGT_sensor_class.py
Author: Kairi Kozumai, Boa-Lin Lai
Date created: 02/17/2017
Date last modified: 02/17/2017
Python Version: 2.7.11
'''
import json

class Sensor(object):
    def __init__(self, name, serialnumber, units, conversion_func):
        # 
        self.name = name
        self.serialnumber = serialnumber
        self.units = units # String in units
        self.conv_func = conversion_func # Function to convert value to meaningful units
        self.value = 0.0 # Default value is 0
    def set_value(self, value):
        self.value = value
    def to_json_string(self):
        value_in_units = self.conv_func(self.value) # Convert to meaningful units
        data = dict(
            name=self.name,
            serialnumber=self.serialnumber,
            units=self.units,
            value=self.value
        )
        return json.dumps(data)    

