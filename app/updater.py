#!/usr/bin/python

'''
File name: updater.py
Author: Boa-Lin Lai, Kairi Kozuma
Date created: 02/20/2017
Date last modified: 02/20/2017
Python Version: 2.7.11
'''

import logging
logging.basicConfig()
from ESGT_data.mbed_sensor import MbedSensor
from ESGT_data.open_weather_map import OpenWeatherMap
import sqlalchemy

import ESGT_database
from ESGT_database.database import DatabaseHelper

from apscheduler.schedulers.blocking import BlockingScheduler
from tzlocal import get_localzone

def update_db_worker(db_helper, name, func_get_json):
    db_helper.insert(name, func_get_json()) #TODO, set name dynamically

def main():
    # Database name to connect to
 
    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    db_helper = DatabaseHelper(host, user, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    db_helper.insert('humidity', {'val':.900})
    db_helper.insert('humidity', {'val':.901})
    db_helper.insert('humidity', {'val':.902})
    db_helper.insert('humidity', {'val':.903})
    db_helper.insert('temperature', {'val':.903})

    # Initialize objects TODO: Use static?
    owm = OpenWeatherMap()
    #mbed = MbedSensor()

    # Initialize job list
    job_list = [
        #{'name': 'light_sensor', 'func': mbed.get_json, 'sec': 5},
        {'name': 'weather', 'func': owm.get_json, 'sec': 5}
    ]

    # Scheduler for updating values
    #scheduler = BlockingScheduler(timezone=get_localzone()) # TODO: Cannot get time inside Docker
    scheduler = BlockingScheduler(timezone='EST')

    # Start jobs
    for job in job_list:
        scheduler.add_job(update_db_worker, 'interval', [db_helper, job['name'], job['func']], seconds=job['sec']);
        print('Launched job')

    scheduler.start() # Blocking call

if __name__ == "__main__":
    main()
