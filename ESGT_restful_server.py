##!/usr/bin/python

'''
File name: ESGT_restful_server.py
Author: Kairi Kozuma
Date created: 02/16/2017
Date last modified: 02/17/2017
Python Version: 2.7.11
'''

# Python restful api
from flask import Flask, request
from flask_restful import Resource, Api

import ESGT_database_interface
from ESGT_database_interface import ESGTDatabase
import json
import random

app = Flask(__name__)
api = Api(app)
'''
# Attempt to change default json encoder to handle datetime
@api.representation('application/json')
def output_json(data, code, headers=None):
    #resp = api.make_response(json.dumps(data), code)
    resp = api.make_response(json.dumps(data, cls=DatetimeEncoder), code)
    resp.headers.extend(headers or {})
    return resp
'''
def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


class ESGTRestfulServer(Resource):
    def get(self, sensor):
        rows = esgt_db.select_backlog_data(sensor)
        # rows = esgt_db.select_sensor_data(sensor)
        # TODO: Handle in json serializer
        print json.dumps(rows[0], default=date_handler)

        return json.loads(json.dumps(rows[0], default=date_handler))

    def put(self, sensor):
        esgt_db.insert_sensor_data(sensor, request.form['data'])
        return #TODO return something

api.add_resource(ESGTRestfulServer, '/<string:sensor>')

if __name__ == '__main__':

    # Instantiate database
    esgt_db = ESGTDatabase(ESGT_database_interface.DB_ESGT)
    esgt_db.initialize()

    app.run(debug=True)
