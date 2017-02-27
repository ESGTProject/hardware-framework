#!/usr/bin/python

'''
File name: models.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 2.7.11
'''

# TODO: Sphinx documentation
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from sqlalchemy.dialects.postgresql import insert

from datetime import datetime

# Database configuration
DB_DEFAULT = 'postgres'
PASS_DEFAULT = 'postgres'
DB_ESGT = 'esgt'

HOST = 'postgres'
USER = 'postgres'

Base = declarative_base()

class Backlog(Base):
    __tablename__ = 'backlog'
    id = Column(Integer, primary_key=True)
    value = Column(JSON, nullable=False)
    create_time = Column(DateTime, nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    resource = relationship('Resource')

    def __repr__(self): #TODO: Do join
        return "<BackLog(name='{}', value='{}', create_time='{}')>".format(self.resource_id, self.value, self.create_time)

class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    value = Column(JSON, nullable=False)
    create_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Resource(name='{}', value='{}', create_time='{}')>".format(self.name, self.value, self.create_time)

# Create database
def create_database():
    engine = sqlalchemy.create_engine("postgres://{}@{}/{}".format(USER, HOST, DB_DEFAULT), echo=True)
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("CREATE DATABASE {}".format(DB_ESGT))
    conn.close()

def create_tables(engine):
    Base.metadata.create_all(engine, checkfirst=True)

def drop_tables(engine):
    Base.metadata.drop_all(engine, checkfirst=True)
    
def insert_into_database(conn, name, value):
    now = datetime.now()
    insert_resource_stmt = insert(Resource.__table__).values(name=name, value=value, create_time=now) #TODO: Insert with valid id
    update_stmt = insert_resource_stmt.on_conflict_do_update(
        index_elements=['name'],
        set_=dict(value=value)
    )
    result = conn.execute(update_stmt)
    insert_backlog_stmt = insert(Backlog.__table__).values(resource_id=result.inserted_primary_key[0], value=value, create_time=now)
    conn.execute(insert_backlog_stmt)

def main():

    engine = sqlalchemy.create_engine("postgres://{}@{}/{}".format(USER, HOST, DB_DEFAULT), echo=True)
    conn = engine.connect()
    metadata=MetaData(bind=engine) 
    Session = sessionmaker(bind=engine)
    session = Session() #TODO Purpose?
   
    # Create tables if needed
    drop_tables(engine)
    create_tables(engine)

    insert_into_database(conn, 'humidity', {'val':.900})
    insert_into_database(conn, 'humidity', {'val':.901})
    insert_into_database(conn, 'humidity', {'val':.902})
    insert_into_database(conn, 'humidity', {'val':.903})
    insert_into_database(conn, 'temperature', {'val':.903})

    for instance in session.query(Backlog).order_by(Backlog.create_time):
        print (instance)

    for instance in session.query(Resource).order_by(Resource.create_time):
        print (instance)

if __name__ == "__main__":
    main()
