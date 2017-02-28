#!/usr/bin/python

'''
File name: app.py
Author: Kairi Kozuma
Date created: 02/16/2017
Date last modified: 02/18/2017
Python Version: 2.7.11
'''

# Python restful api
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import sqlalchemy
import json

import ESGT_database
from ESGT_database.database import DatabaseHelper

app = Flask(__name__)
api = Api(app)
CORS(app) # Enable CORS
db_helper = None

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

def flatten(row):
    dct = json.loads(row.value)
    dct["timestamp"] = row.time_created
    return dct

class Resource(Resource):
    def get(self, resource):
        limit_str = request.args.get('limit')
        limit = int(limit_str) if limit_str != None else 10 #TODO: Handle error
        rows = db_helper.select(resource, limit)
        if rows is not None:
            elem_array = list(map(flatten, rows))
            return json.loads(json.dumps(elem_array, default=date_handler))

    def put(self, resource):
        return #TODO return something

class ResourceList(Resource):
    def get(self):
        rows = db_helper.select_resources()
        return rows

    def put(self):
        return #TODO: return something

api.add_resource(Resource, '/resource/<string:resource>')
api.add_resource(ResourceList, '/resource')

if __name__ == '__main__':

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    db_helper = DatabaseHelper(host, user, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    app.run(debug=True, host="0.0.0.0", port=8000)
    #app.run(debug=True, host="localhost", port=8000)

