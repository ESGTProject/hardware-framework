#!/usr/bin/python

'''
File name: models.py
Author: Kairi Kozuma
Date created: 02/27/2017
Date last modified: 02/27/2017
Python Version: 2.7.11
'''

# TODO: Sphinx documentation
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
class Backlog(Base):
    __tablename__ = 'backlog'
    id = Column(Integer, primary_key=True)
    value = Column(JSON, nullable=False)
    create_time = Column(DateTime, nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    resource = relationship('Resource')

    def __repr__(self):
        return "<BackLog(resource_id='{}', value='{}', create_time='{}')>".format(self.resource_id, self.value, self.create_time)

class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    value = Column(JSON, nullable=False)
    create_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Resource(name='{}', value='{}', create_time='{}')>".format(self.name, self.value, self.create_time)
