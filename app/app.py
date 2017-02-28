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

class ESGTRestfulServer(Resource):
    def get(self, resource):
        rows = db_helper.select(resource)
        if rows is not None:
            return json.loads(json.dumps(r.__dict__ for r in rows))
            #elem_array = [None] * len(rows)
            # for i, row in enumerate(rows): # Flatten timestamp and JSON
            #     obj = row.value
            #     obj["timestamp"] = row.time_created
            #     elem_array[i] = obj
            #return json.loads(json.dumps(rows, default=date_handler))

    def put(self, resource):
        return #TODO return something

api.add_resource(ESGTRestfulServer, '/<string:resource>')

if __name__ == '__main__':

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    db_helper = DatabaseHelper(host, user, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    app.run(debug=True, host="0.0.0.0", port=8000)
    #app.run(debug=True, host="localhost", port=8000)

