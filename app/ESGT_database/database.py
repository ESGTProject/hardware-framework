#!/usr/bin/python

'''
File name: database.py
Author: Kairi Kozuma
Date created: 02/08/2017
Date last modified: 02/18/2017
Python Version: 2.7.11
'''

# TODO: Sphinx documentation

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import random
import json
import time
# import pgpasslib #TODO need password file if not default user

# Formatting strings
conn_template = "host='{}' user='{}' dbname='{}'"
conn_template_pass = "host='{}' user='{}' password='{}' dbname='{}'"

# Database configuration
DB_DEFAULT = 'postgres'
PASS_DEFAULT = 'postgres'
DB_ESGT = 'esgt'

class PostgreSQLDatabase(object):
    def __init__(self, host, user, database_name):
        self.db_name = database_name
        self.conn_db = None
        self.conn_db_config = conn_template.format(host, user, database_name)
        self.conn_db_config_default = conn_template.format(host, user, DB_DEFAULT)

    # Check connection to database
    def connect_database(self):
        try:
            self.conn_db = psycopg2.connect(self.conn_db_config)
        except psycopg2.Error as e:
            print "Unable to connect to the database {}".format(self.db_name)
            print e
            print "Attempting to create database {}".format(self.db_name)
            try:
                self.create_database()
                print "Created database {}".format(self.db_name)
                self.connect_database()
            except psycopg2.Error as e:
                print "Could not create database {}".format(self.db_name)
                print e

    # Create database if it does not exist
    def create_database(self):
        with psycopg2.connect(self.conn_db_config_default) as conn:
            # Enable autocommit to avoid transaction error when creating database
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                query = 'CREATE DATABASE {}'.format(self.db_name)
                cur.execute(query)
            conn.commit()

    # Delete database
    def delete_database(self):
        with psycopg2.connect(self.conn_db_config_default) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                query = 'DROP DATABASE IF EXISTS {}'.format(self.db_name)
                cur.execute(query)
            conn.commit()

    # Clears contents of a given table 'table_name'
    def clear_table(self, table_name):
        if (self.conn_db is not None) or (self.connect_database() is not None):
            with self.conn_db.cursor() as cur:
                query = 'TRUNCATE TABLE {}'.format(table_name)
                cur.execute(query)
            self.conn_db.commit()


class ESGTDatabase(PostgreSQLDatabase):
    # Backlog table
    TABLE_BACKLOG = 'backlog'
    COL_BACKLOG_ID = 'id'
    COL_BACKLOG_SENSOR_KEY = 'sensor_key'
    COL_BACKLOG_VALUE = 'value'
    COL_BACKLOG_CREATE_TIME = 'create_time'

    # Backlog table
    TABLE_SENSORS = 'sensors'
    COL_SENSORS_ID = 'id'
    COL_SENSORS_NAME = 'name'
    COL_SENSORS_VALUE = 'value'
    COL_SENSORS_CREATE_TIME = 'create_time'

    # Initialization function (connect to database, create table if necessary)
    def initialize(self):
        # Connect to database
        self.connect_database()

        # Create tables if not present
        self.create_sensor_table() # Must be called before creating backlog table
        self.create_backlog_table()

    # Create sensor table
    def create_sensor_table(self):
        if (self.conn_db is not None) or (self.connect_database() is not None):
            with self.conn_db.cursor() as cur:
                query = 'CREATE TABLE IF NOT EXISTS PUBLIC.{} (    \
                    {} SERIAL NOT NULL PRIMARY KEY,  \
                    {} VARCHAR(50) UNIQUE NOT NULL,  \
                    {} JSON NOT NULL,                \
                    {} TIMESTAMP NOT NULL            \
                    )'.format(self.TABLE_SENSORS,
                              self.COL_SENSORS_ID,
                              self.COL_SENSORS_NAME,
                              self.COL_SENSORS_VALUE,
                              self.COL_SENSORS_CREATE_TIME)
                cur.execute(query)
            self.conn_db.commit()
        else:
            print ("ERROR: Could not establish connection to database")

    # Create backlog table
    def create_backlog_table(self):
        if (self.conn_db is not None) or (self.connect_database() is not None):
            with self.conn_db.cursor() as cur:
                query = 'CREATE TABLE IF NOT EXISTS PUBLIC.{} (          \
                    {} SERIAL NOT NULL PRIMARY KEY,        \
                    {} INTEGER NOT NULL REFERENCES {}({}), \
                    {} JSON NOT NULL,                      \
                    {} TIMESTAMP NOT NULL                  \
                    )'.format(self.TABLE_BACKLOG,
                              self.COL_BACKLOG_ID,
                              self.COL_BACKLOG_SENSOR_KEY, self.TABLE_SENSORS, self.COL_SENSORS_ID,
                              self.COL_BACKLOG_VALUE,
                              self.COL_BACKLOG_CREATE_TIME)
                cur.execute(query)
            self.conn_db.commit()
        else:
            print ("ERROR: Could not establish connection to database")

    # Insert sensor 'sensor' and 'value' to the database, along with timestamp
    # Simultaneously inserts it into 'backlog' table and 'sensors' table
    def insert_sensor_data(self, sensor, value):
        if (self.conn_db is not None) or (self.connect_database() is not None):
            with self.conn_db.cursor() as cur:
                # Get time stamp
                timestamp_now = datetime.now()

                # Insert into current sensors table #TODO: Clean up text formatting references
                query = "INSERT INTO {} ({},{},{}) VALUES (%s, %s, %s)\
                         ON CONFLICT ({}) DO UPDATE SET {} = (%s), {} = (%s) ".format(
                    self.TABLE_SENSORS,
                    self.COL_SENSORS_NAME,
                    self.COL_SENSORS_VALUE,
                    self.COL_SENSORS_CREATE_TIME,
                    self.COL_SENSORS_NAME,
                    self.COL_SENSORS_VALUE,
                    self.COL_SENSORS_CREATE_TIME)

                data = (sensor, value, timestamp_now, value, timestamp_now)  # TODO: Fix duplicates
                cur.execute(query, data)

                # Get sensor key id
                query = "SELECT {} FROM {} WHERE {} = %s".format(
                    self.COL_SENSORS_ID,
                    self.TABLE_SENSORS,
                    self.COL_SENSORS_NAME)
                data = (sensor,)
                cur.execute(query, data)
                id = cur.fetchall()[0]  # Get id of foreign key

                # Insert into backlog table
                query = "INSERT INTO {} ({},{},{}) VALUES (%s, %s, %s)".format(
                    self.TABLE_BACKLOG,
                    self.COL_BACKLOG_SENSOR_KEY,
                    self.COL_BACKLOG_VALUE,
                    self.COL_BACKLOG_CREATE_TIME)
                data = (id, value, timestamp_now)
                cur.execute(query, data)

            self.conn_db.commit()

    # Retrieve value for sensor name
    def select_sensor_data(self, sensor):
        if (self.conn_db is not None) or (self.connect_database() is not None):
            with self.conn_db.cursor() as cur:
                query = "SELECT {}, {} from {} where {} = (%s) ORDER BY {} DESC".format(
                    self.COL_SENSORS_VALUE,
                    self.COL_SENSORS_CREATE_TIME,
                    self.TABLE_SENSORS,
                    self.COL_SENSORS_NAME,
                    self.COL_SENSORS_CREATE_TIME)
                data = (sensor,)
                cur.execute(query, data)
                rows = cur.fetchall()
            self.conn_db.commit()
            return rows

    # Retrieve backlog values for sensor name
    def select_backlog_data(self, sensor):
        if (self.conn_db is not None) or (self.connect_database() is not None):
            with self.conn_db.cursor() as cur:
                # TODO: Make query constant and easier to read
                query = "SELECT {}, {} from {} JOIN {} ON {}={} where {} = (%s) ORDER BY {} DESC".format(
                    self.TABLE_BACKLOG + "." + self.COL_BACKLOG_VALUE,
                    self.TABLE_BACKLOG + "." + self.COL_BACKLOG_CREATE_TIME,
                    self.TABLE_BACKLOG,
                    self.TABLE_SENSORS,
                    self.TABLE_SENSORS + "." + self.COL_SENSORS_ID,
                    self.TABLE_BACKLOG + "." + self.COL_BACKLOG_SENSOR_KEY,
                    self.COL_SENSORS_NAME,
                    self.TABLE_BACKLOG + "." + self.COL_BACKLOG_CREATE_TIME)
                data = (sensor,)
                cur.execute(query, data)
                rows = cur.fetchall()
            self.conn_db.commit()
            return rows

def main():
    # Database name to connect to
    db_name = DB_ESGT

    # Instantiate database
    esgt_db = ESGTDatabase(db_name)
    esgt_db.initialize()

    # Test inserting sensor values
    sensor_names = ['light_sensor', 'temp_sensor', 'proximity_sensor']
    sensor_units = ['lumens', 'C', 'cm']
    print "Insert 10 random entries and retrieve them\n"
    for i in range(20):
        for index, sen in enumerate(sensor_names):
            randval = 10 * i + 100 * random.uniform(0, 5.0)
            jsonstr = json.dumps({'units': sensor_units[index], 'value': randval})
            esgt_db.insert_sensor_data(sen, jsonstr)
        time.sleep(0.25)

    rows = esgt_db.select_sensor_data('light_sensor')
    for row in rows:
       print "value = ", row[0]
       print "timestamp = ", row[1], "\n"

    print "Total entries: ", len(rows)

if __name__ == "__main__":
    main()
