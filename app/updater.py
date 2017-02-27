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
import ESGT_database.database
from ESGT_database.database import ESGTDatabase
from ESGT_data.mbed_sensor import MbedSensor
from ESGT_data.open_weather_map import OpenWeatherMap

from apscheduler.schedulers.blocking import BlockingScheduler
from tzlocal import get_localzone

def update_db_worker(database, name, func_get_json):
    database.insert_sensor_data(name, func_get_json()) #TODO, set name dynamically

def main():
    # Database name to connect to
    db_name = ESGT_database.database.DB_ESGT

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    esgt_db = ESGTDatabase(host, user, db_name)
    esgt_db.initialize()

    # Initialize objects TODO: Use static?
    owm = OpenWeatherMap()
    mbed = MbedSensor()

    # Initialize job list
    job_list = [
        {'name': 'weather', 'func': owm.get_json, 'sec': 120},
        {'name': 'light_sensor', 'func': mbed.get_json, 'sec': 5}
    ]

    # Scheduler for updating values
    #scheduler = BlockingScheduler(timezone=get_localzone()) # TODO: Cannot get time inside Docker
    scheduler = BlockingScheduler(timezone='EST')

    # Start jobs
    for job in job_list:
        scheduler.add_job(update_db_worker, 'interval', [esgt_db, job['name'], job['func']], seconds=job['sec']);
        print('Launched job')

    scheduler.start() # Blocking call

if __name__ == "__main__":
    main()

