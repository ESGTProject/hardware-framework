#!/bin/python
'''
File name: setup.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 2.7.11
'''

from ESGT_database import database as ESGT_DB
from ESGT_database.database import DatabaseHelper
import sqlalchemy

def main():
    # Create database and tables
    db_helper = DatabaseHelper(ESGT_DB.USER_DEFAULT, ESGT_DB.HOST_DEFAULT, ESGT_DB.DB_ESGT)
    try:
        db_helper.create_database()
    except sqlalchemy.exc.ProgrammingError:
        print ("Database already exists")
    db_helper.connect()
    db_helper.drop_tables() #TODO: Offer cleaning function
    db_helper.create_tables()

if __name__ == "__main__":
    main()
