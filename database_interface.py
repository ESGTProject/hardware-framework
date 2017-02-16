#!/usr/bin/python

'''
File name: database_interface.py
Author: Kairi Kozuma
Date created: 02/08/2017
Date last modified: 02/16/2017
Python Version: 2.7.11
'''

# TODO: Sphinx documentation

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import random
import json
# import pgpasslib #TODO need password file if not default user

# Formatting strings
conn_template = "host='{}' dbname='{}' user='{}'"

# Database configuration
# PostgreSQL server hosts
HOST_LOCALHOST = 'localhost'
# PostgreSQL users
USER_POSTGRES = 'postgres'
# Database names
DB_POSTGRES = 'postgres'
DB_ESGT = 'esgt'

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

# Connection strings used by psycopg2
CONN_DEFAULT = conn_template.format(HOST_LOCALHOST, DB_POSTGRES, USER_POSTGRES)


# Check connection to database
def connect_database(db_name):
    conn_db = conn_template.format(HOST_LOCALHOST, db_name, USER_POSTGRES)
    try:
        return psycopg2.connect(conn_db)
    except psycopg2.Error as e:
        print "Unable to connect to the database {}".format(db_name)
        print e
        return None


# Create database 'db_name' if it does not exist
def create_database(db_name):
    with psycopg2.connect(CONN_DEFAULT) as conn:
        # Enable autocommit to avoid transaction error when creating database
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            query = 'CREATE DATABASE {}'.format(db_name)
            cur.execute(query)
        conn.commit()


# Delete database given by 'db_name'
def delete_database(db_name):
    with psycopg2.connect(CONN_DEFAULT) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            query = 'DROP DATABASE IF EXISTS {}'.format(db_name)
            cur.execute(query)
        conn.commit()


# Clears contents of a given table 'table_name'
def clear_table(conn, table_name):
    with conn.cursor() as cur:
        query = 'TRUNCATE TABLE {}'.format(table_name)
        cur.execute(query)
    conn.commit()


# ESGT specific functions
# Create sensor table
def create_sensor_table(conn):
    with conn.cursor() as cur:
        query = 'CREATE TABLE IF NOT EXISTS PUBLIC.{} (    \
            {} SERIAL NOT NULL PRIMARY KEY,  \
            {} VARCHAR(50) UNIQUE NOT NULL,  \
            {} JSON NOT NULL,                \
            {} TIMESTAMP NOT NULL            \
            )'.format(TABLE_SENSORS,
                COL_SENSORS_ID,
                COL_SENSORS_NAME,
                COL_SENSORS_VALUE,
                COL_SENSORS_CREATE_TIME)
        cur.execute(query)
    conn.commit()


# Create backlog table
def create_backlog_table(conn):
    with conn.cursor() as cur:
        query = 'CREATE TABLE IF NOT EXISTS PUBLIC.{} (          \
            {} SERIAL NOT NULL PRIMARY KEY,        \
            {} INTEGER NOT NULL REFERENCES {}({}), \
            {} JSON NOT NULL,                      \
            {} TIMESTAMP NOT NULL                  \
            )'.format(TABLE_BACKLOG,
                COL_BACKLOG_ID,
                COL_BACKLOG_SENSOR_KEY, TABLE_SENSORS, COL_SENSORS_ID,
                COL_BACKLOG_VALUE,
                COL_BACKLOG_CREATE_TIME)
        cur.execute(query)
    conn.commit()

# Insert sensor 'sensor' and 'value' to the database, along with timestamp
# Simultaneously inserts it into 'backlog' table and 'sensors' table
def insert_sensor_data(conn, sensor, value):
    with conn.cursor() as cur:
        # Get time stamp
        timestamp_now = datetime.now()

        # Insert into current sensors table #TODO: Clean up text formatting references
        query = "INSERT INTO {} ({},{},{}) VALUES (%s, %s, %s)\
                 ON CONFLICT ({}) DO UPDATE SET {} = (%s), {} = (%s) ".format(
            TABLE_SENSORS,
            COL_SENSORS_NAME,
            COL_SENSORS_VALUE,
            COL_SENSORS_CREATE_TIME,
            COL_SENSORS_NAME,
            COL_SENSORS_VALUE,
            COL_SENSORS_CREATE_TIME)

        data = (sensor, value, timestamp_now, value, timestamp_now) #TODO: Fix duplicates
        cur.execute(query, data)

        # Get sensor key id
        query = "SELECT {} FROM {} WHERE {} = %s".format(
            COL_SENSORS_ID,
            TABLE_SENSORS,
            COL_SENSORS_NAME)
        data = (sensor,)
        cur.execute(query, data)
        id = cur.fetchall()[0] # Get id of foreign key

        # Insert into backlog table
        query = "INSERT INTO {} ({},{},{}) VALUES (%s, %s, %s)".format(
            TABLE_BACKLOG,
            COL_BACKLOG_SENSOR_KEY,
            COL_BACKLOG_VALUE,
            COL_BACKLOG_CREATE_TIME)
        data = (id, value, timestamp_now)
        cur.execute(query, data)

    conn.commit()


# Retrieve value for sensor name
def select_sensor_data(conn, sensor):
    with conn.cursor() as cur:
        query = "SELECT {}, {} from {} where name = (%s)".format(
            COL_SENSORS_VALUE,
            COL_SENSORS_CREATE_TIME,
            TABLE_SENSORS)
        data = (sensor,)
        cur.execute(query, data)
        rows = cur.fetchall()
    conn.commit()
    return rows


def main():

    # Database name to connect to
    db_name = DB_ESGT

    # Delete database
    #delete_database(db_name)

    # Connect to database
    conn = connect_database(db_name)

    # If connection succeeds, continue
    if conn is not None:
        print "Successfully connected to database {}".format(db_name)
    else: # Else, attempts to create database
        print "Could NOT connect to database {}".format(db_name)
        print "Attempting to create database {}".format(db_name)
        try:
            create_database(db_name)
            conn = connect_database(db_name)
            print "Created database {}".format(db_name)
        except psycopg2.Error as e:
            print "Could not create database {}".format(db_name)
            print e
            quit()

    # Create tables if not present
    create_sensor_table(conn)
    create_backlog_table(conn)

    # Retrieve data from table TODO: User dictionary cursor?
    rows = select_sensor_data(conn, 'light_sensor')
    print "Total entries: ", len(rows)

    # Test inserting sensor values
    sensor_names = ['light_sensor', 'temp_sensor', 'proximity_sensor']
    print "Insert 10 random entries and retrieve them\n"
    for i in range(10):
        for sen in sensor_names:
            randval = 10 * i + random.uniform(0, 5.0)
            jsonstr = json.dumps(['data', {'value': randval}])
            insert_sensor_data(conn, sen, jsonstr)

    rows = select_sensor_data(conn, 'light_sensor')
    for row in rows:
       print "value = ", row[0]
       print "timestamp = ", row[1], "\n"

    print "Total entries: ", len(rows)

if __name__ == "__main__":
    main()
