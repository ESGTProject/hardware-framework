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
from sqlalchemy import desc
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
        self.engine = None

    def connect(self):
        self.engine = sqlalchemy.create_engine("postgres://{}@{}/{}".format(self.user, self.host, self.database), echo=True)

    def create_database(self):
        engine = sqlalchemy.create_engine("postgres://{}@{}/{}".format(self.user, self.host, DB_DEFAULT), echo=True)
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
        now = datetime.utcnow()
        insert_resource_stmt = insert(Resource.__table__).values(name=name, value=value, time_created=now)
        update_stmt = insert_resource_stmt.on_conflict_do_update(
            index_elements=['name'],
            set_=dict(value=value)
        )
        result = conn.execute(update_stmt)
        insert_backlog_stmt = insert(Backlog.__table__).values(resource_id=result.inserted_primary_key[0], value=value, time_created=now)
        conn.execute(insert_backlog_stmt)
        conn.close()

    def select(self, name, limit=50):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        result = session.query(Backlog).join(Resource).filter(Resource.name==name).order_by(desc(Backlog.time_created)).limit(limit).all()
        session.close()
        return result

    def select_resources(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        result = session.query(Resource.name).order_by(Resource.name).all()
        session.close()
        return result