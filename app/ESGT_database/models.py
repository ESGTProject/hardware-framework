#!/usr/bin/python

'''
File name: models.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 2.7.11
'''

# TODO: Sphinx documentation
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
class Backlog(Base):
    __tablename__ = 'backlog'
    id = Column(Integer, primary_key=True)
    value = Column(JSON, nullable=False)
    time_created = Column(DateTime, nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    resource = relationship('Resource')

    def __repr__(self):
        return "<BackLog(resource_id='{}', value='{}', time_created='{}')>".format(self.resource_id, self.value, self.time_created)

class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    value = Column(JSON, nullable=False)
    time_created = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return "<Resource(name='{}', value='{}', time_created='{}')>".format(self.name, self.value, self.time_created)

class Configuration(Base):
    __tablename__ = 'configuration'
    id = Column(Integer, primary_key=True)
    login_email = Column(String, nullable=False, unique=True)
    refresh_tokens = Column(JSON, nullable=False)
    display_name = Column(String, nullable=False)
    news_source = Column(String, nullable=False)
    weather_city = Column(String, nullable=False)
    temperature_units = Column(Boolean, nullable=False)
    time_zone = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), nullable=False)