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
from flask_sqlalchemy import SQLAlchemy

import json

app = Flask(__name__)
api = Api(app)
CORS(app) # Enable CORS
esgt_db = 

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

class ESGTRestfulServer(Resource):
    def get(self, sensor):
        rows = esgt_db.select_backlog_data(sensor)
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

    def put(self, sensor):
        return #TODO return something

api.add_resource(ESGTRestfulServer, '/<string:sensor>')

if __name__ == '__main__':

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    esgt_db = ESGTDatabase(host, user, ESGT_database.database.DB_ESGT)
    esgt_db.initialize()

    app.run(debug=True, host="0.0.0.0", port=8000)
    #app.run(debug=True, host="localhost", port=8000)
