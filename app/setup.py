#!/bin/python
'''
File name: setup.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 3.6.0
'''

from ESGT_database import database as ESGT_DB
from ESGT_database.database import DatabaseHelper
import sqlalchemy
import sys
import json

def main():
    # Create database and tables
    config = None
    with open('config.json') as json_file:
        config = json.load(json_file)
    if config is None:
        raise IOError("Configuration file 'config.json' not found")
    user = config['database']['user']
    password = config['database']['password']
    host = config['database']['host']
    db_helper = DatabaseHelper(user, password, host, ESGT_DB.DB_ESGT)
    try:
        db_helper.create_database()
    except sqlalchemy.exc.ProgrammingError:
        print ("Database already exists")
    db_helper.connect()
    # Option to clean tables with setup.py clean
    if (len(sys.argv) < 1 and sys.argv[1] == 'clean'):
        db_helper.drop_tables()
    db_helper.create_tables()

if __name__ == "__main__":
    main()
