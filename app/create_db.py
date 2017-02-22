#!/usr/bin/python

'''
File name: create_db.py
Author: Kairi Kozuma
Date created: 02/18/2017
Date last modified: 02/18/2017
Python Version: 2.7.11
'''

import ESGT_database.database
from ESGT_database.database import ESGTDatabase
import random
import json

def main():
    # Database name to connect to
    db_name = ESGT_database.database.DB_ESGT

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    esgt_db = ESGTDatabase(host, user, db_name)
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
