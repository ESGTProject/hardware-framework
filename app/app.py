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

app = Flask(__name__)
api = Api(app)
CORS(app) # Enable CORS
esgt_db = None

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

class ESGTRestfulServer(Resource):
    def get(self, resource):
        rows = esgt_db.select(resource)
        if rows is not None:
            if len(rows) > 50: #TODO: Allow dynamic query, temp:Truncate to first 50
                rows = rows[:50]
            elem_array = [None] * len(rows)
            for i, row in enumerate(rows):
                dict = row[0]
                dict["timestamp"] = row[1]
                elem_array[i] = dict
            return json.loads(json.dumps(elem_array, default=date_handler))
        else:
            return

    def put(self, resource):
        return #TODO return something

api.add_resource(ESGTRestfulServer, '/<string:resource>')

if __name__ == '__main__':

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    esgt_db = DatabaseHelper(host, user, ESGT_database.database.DB_ESGT)

    app.run(debug=True, host="0.0.0.0", port=8000)
    #app.run(debug=True, host="localhost", port=8000)

    db_helper.insert('humidity', {'val':.900})
    db_helper.insert('humidity', {'val':.901})
    db_helper.insert('humidity', {'val':.902})
    db_helper.insert('humidity', {'val':.903})
    db_helper.insert('temperature', {'val':.903})
