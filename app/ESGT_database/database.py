#!/bin/python

'''
File name: database.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 2.7.11
'''

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime

from .models import Base, Resource, Backlog

# Database configuration
USER_DEFAULT = 'postgres'
HOST_DEFAULT = 'postgres'
DB_ESGT = 'esgt'
DB_DEFAULT = 'postgres'

class DatabaseHelper(object):
    def __init__(self, user, host, database):
        self.user = user
        self.host = host
        self.database = database
        self.engine = sqlalchemy.create_engine("postgres://{}@{}/{}".format(user, host, database), echo=True)

    def create_database(self):
        self.engine = create_engine(self.user, self.host, DB_DEFAULT)
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("CREATE DATABASE {}".format(self.database))
        conn.close()

    def create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine, checkfirst=True)
        
    def insert(self, name, value):
        conn = self.engine.connect()
        now = datetime.now()
        insert_resource_stmt = insert(Resource.__table__).values(name=name, value=value, create_time=now)
        update_stmt = insert_resource_stmt.on_conflict_do_update(
            index_elements=['name'],
            set_=dict(value=value)
        )
        result = conn.execute(update_stmt)
        insert_backlog_stmt = insert(Backlog.__table__).values(resource_id=result.inserted_primary_key[0], value=value, create_time=now)
        conn.execute(insert_backlog_stmt)
        conn.close()

    def select(self, name):
        return session.query(Backlog).join(Resource).filter(Resource.name==name).order_by(Backlog.create_time)