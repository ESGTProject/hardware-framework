#!/usr/bin/python

'''
File name: ESGT_setup.py
Author: Kairi Kozuma
Date created: 02/18/2017
Date last modified: 02/18/2017
Python Version: 2.7.11
'''

import ESGT_database_interface
from ESGT_database_interface import ESGTDatabase
import random
import json

def main():
    # Database name to connect to
    db_name = ESGT_database_interface.DB_ESGT

    # Instantiate database
    esgt_db = ESGTDatabase(db_name)
    esgt_db.initialize()

    # Test inserting sensor values
    sensor_names = ['light_sensor', 'temp_sensor', 'proximity_sensor']
    sensor_units = ['lumens', 'C', 'cm']
    for i in range(20):
        for index, sen in enumerate(sensor_names):
            randval = 10 * i + 100 * random.uniform(0, 5.0)
            jsonstr = json.dumps({'units': sensor_units[index], 'value': randval})
            esgt_db.insert_sensor_data(sen, jsonstr)

if __name__ == "__main__":
    main()
