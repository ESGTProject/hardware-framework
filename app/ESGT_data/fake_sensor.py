##!/usr/bin/python
'''
File name: fake_sensor.py
Author: Kairi Kozuma
Date created: 02/28/2017
Date last modified: 02/28/2017
Python Version: 2.7.11
'''
from .sensor import Sensor
import random
from datetime import datetime

class FakeSensor(Sensor):
    def to_json_string(self):
        random.seed(datetime.now())
        self.value = random.random()
        return Sensor.to_json_string(self)
