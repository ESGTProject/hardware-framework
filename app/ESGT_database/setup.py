#!/bin/python
'''
File name: setup.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 2.7.11
'''

import .database

def main():
    # Create database and tables
    db_helper = DatabaseHelper(database.USER_DEFAULT, database.HOST_DEFAULT, database.DB_ESGT)
    db_helper.create_database()
    db_helper.create_tables()

if __name__ == "__main__":
    main()
