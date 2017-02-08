#!/usr/bin/python

'''
File name: database_interface.py
Author: Kairi Kozuma
Date created: 02/08/2017
Date last modified: 02/08/2017
Python Version: 2.7.11
'''

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import random
# import pgpasslib #TODO need password?
# password = pgpasslib.getpass('localhost', 5432, 'postgres', 'postgres')

# Database configuration
db_default = "host='localhost' dbname='postgres' user='postgres'"
db_esgt = "host='localhost' dbname='esgt' user='postgres'"
DB_ESGT_NAME = 'esgt'

# Open connection to local database, creating one if necessary
def check_database_exists():
    # Test connection to database TODO
    with psycopg2.connect(db_default) as con:
        with con.cursor() as cur:
            query = 'SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s)'
            cur.execute(query, [DB_ESGT_NAME])
            answer = cur.fetchall()
    print (answer)
    if answer[0][0]:
        print "Database {} exists".format(DB_ESGT_NAME)
        return True
    else:
        print "Database {} does NOT exist".format(DB_ESGT_NAME)
        return False

def create_database():
    # Create database if it does not exist
    # TODO: Handle errors
    with psycopg2.connect(db_default) as con:
        # Enable autocommit to avoid transaction error when creating database
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with con.cursor() as cur:
            query = 'CREATE DATABASE %s;'
            cur.execute(query % DB_ESGT_NAME)
            #query = 'CREATE DATABASE esgt'
            #cur.execute(query)
            #cur.execute(query, ['esgt'])

def create_sensor_table():
    with psycopg2.connect(db_esgt) as con:
        with con.cursor() as cur:
            cur.execute('''CREATE TABLE SENSOR_DATA
               (id         SERIAL PRIMARY KEY     NOT NULL,
               name        CHAR(50),
               ts          TIMESTAMP,
               value       REAL);''')

def insert_sensor_data(name, value):
    with psycopg2.connect(db_esgt) as con:
        with con.cursor() as cur:
            query = '''INSERT INTO SENSOR_DATA (name,value,ts) \
                VALUES (%s, %s, %s)'''
            cur.execute(query, (name, value, datetime.now()))

def select_sensor_data(name):
    with psycopg2.connect(db_esgt) as con:
        with con.cursor() as cur:
            query = 'SELECT id, name, ts, value from SENSOR_DATA where name = (%s);'
            cur.execute(query, (name,))
            rows = cur.fetchall()
    return rows;

def delete_sensor_data(name):
    with psycopg2.connect(db_esgt) as con:
        with con.cursor() as cur:
            query = '''DELETE from SENSOR_DATA where name = (%s)'''
            cur.execute(query, (name,)) #TODO: Fix redundancy
            print "Total number of rows deleted :", cur.rowcount

if check_database_exists():
    # Insert random data into table
    print "Press enter to insert 10 random entries and retrieve them\n"
    raw_input();
    for i in range(10):
        insert_sensor_data('light_sensor', 10 * i + random.uniform(0, 5.0))

    # Retrieve data from table TODO: User dictionary cursor?
    rows = select_sensor_data('light_sensor');
    for row in rows:
       print "id = ", row[0]
       print "name = ", row[1]
       print "ts = ", row[2]
       print "value = ", row[3], "\n"

    # Delete from table
    print "Press enter to delete entries\n"
    raw_input(); # Wait for user input
    rows = delete_sensor_data('light_sensor');
    rows = select_sensor_data('light_sensor');
    for row in rows:
       print "id = ", row[0]
       print "name = ", row[1]
       print "ts = ", row[2]
       print "value = ", row[3], "\n"

else:
    # Create database and table
    create_database()
    create_sensor_table() # TODO: Create if table does not exist with SQL
    print "Database and table created\n"
