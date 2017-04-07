#!/usr/bin/python

'''
File name: updater.py
Author: Boa-Lin Lai, Kairi Kozuma
Date created: 02/20/2017
Date last modified: 03/29/2017
Python Version: 3.6.0
'''

import logging
logging.basicConfig()
import sqlalchemy
import json
from ESGT_data.mbed_sensor import MbedSensor
from ESGT_data.sensor import Sensor
from ESGT_data.fake_sensor import FakeSensor
import ESGT_database
from ESGT_database.database import DatabaseHelper

from apscheduler.schedulers.blocking import BlockingScheduler

class Job(object):
    def __init__(self, name, json_func, sec_interval):
        self.name = name
        self.json_func = json_func
        self.sec_interval = sec_interval

def update_db_worker(db_helper, job):
    """Function to insert json into database

    Arguments:
        db_helper : DatabaseHelper instance to connect to database
        job : Job object with name, json retrieval function, and time interval
    """
    db_helper.insert(job.name, job.json_func())

def main():
    # Instantiate database helper
    config = None
    with open('config.json') as json_file:
        config = json.load(json_file)
    if config is None:
        raise IOError("Configuration file 'config.json' not found")
    user = config['database']['user']
    password = config['database']['password']
    host = config['database']['host']
    db_helper = DatabaseHelper(user, password, host, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    mbed = MbedSensor()

    # Initialize job list
    job_list = [
        Job('light', mbed.get_json_light, 5),
        Job('humidity', mbed.get_json_humidity, 7),
        Job('temperature', mbed.get_json_temperature, 10)
    ]

    # Create fake data for testing #TODO: Handle dynamically
    fake_data = False
    if fake_data:
        light_sensor = FakeSensor('light', 'HAL9000', 'lux', lambda x: x * 10000)
        temperature_sensor = FakeSensor('temperature', 'TMPSNSR451', 'degreesC', lambda x: x * 32)
        humidity_sensor = FakeSensor('humidity', 'HMD9999', 'percent', lambda x: x * 100)

        job_list.append(Job('light', light_sensor.to_json_string, 60))
        job_list.append(Job('temperature', temperature_sensor.to_json_string, 60))
        job_list.append(Job('humidity', humidity_sensor.to_json_string, 60))

    # Scheduler for updating values
    scheduler = BlockingScheduler(timezone='EST')

    # Start jobs
    for job in job_list:
        scheduler.add_job(update_db_worker, 'interval', [db_helper, job], seconds=job.sec_interval)
        print('Launched job:{}'.format(job.name))

    scheduler.start() # Blocking call

if __name__ == "__main__":
    main()
