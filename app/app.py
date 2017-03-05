#!/usr/bin/python

'''
File name: app.py
Author: Kairi Kozuma
Date created: 02/16/2017
Date last modified: 03/01/2017
Python Version: 2.7.11
'''

from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import sqlalchemy
import json
import pytz
import requests

import ESGT_database
from ESGT_database.database import DatabaseHelper

# Set up flask app variables
app = Flask(__name__)
api = Api(app)
CORS(app) # Enable CORS

# Default number of items to return
DEFAULT_RESOURCE_LENGTH = 10

# Database helper for backend postgresql
db_helper = None

# Non database helper for other (non database backed up) resources
nondb_resource_dict = {}

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

def flatten(row):
    dct = json.loads(row.value)
    dct["timestamp"] = pytz.utc.localize(row.time_created, is_dst=None).astimezone(pytz.utc)
    return dct

class Resource(Resource):
    def get(self, resource):
        # If it is a nondatabase resource, attempt query
        if resource in nondb_resource_dict.keys():
            args = request.args
            return nondb_resource_dict[resource].get(args)

        else: # Use database to build response
            limit_str = request.args.get('limit')
            limit = int(limit_str) if limit_str is not None else DEFAULT_RESOURCE_LENGTH
            rows = db_helper.select(resource, limit)
            if rows is not None:
                elem_array = list(map(flatten, rows))
                return json.loads(json.dumps(elem_array, default=date_handler))

    def put(self, resource):
        return

class ResourceList(Resource):
    def get(self):
        # List of resources from database
        list_of_lists = db_helper.select_resources()
        resource_list = [v for sublist in list_of_lists for v in sublist] # Flatten list of lists
        # Add list of resources from non database resources
        resource_list.extend(nondb_resource_dict.keys())
        return resource_list

    def put(self):
        return

class NoDatabaseResource(object):
    def __init__(self, name, endpoint, api_key_query, api_key):
        self.name = name
        self.endpoint = endpoint
        self.api_key_query = api_key_query
        self.api_key = api_key


class NewsAPIResource(NoDatabaseResource): #TODO: Move to own file in module
    def get(self, params = {}):
        params = params.to_dict()
        params[self.api_key_query] = self.api_key # add api key to params
        try:
            r = requests.get(self.endpoint, params)
            return r.json()['articles']
        except:
            print ("Error retrieving data for {} at {}".format(self.name, self.endpoint))
            return None

# Add api endpoints
api.add_resource(Resource, '/resource/<string:resource>')
api.add_resource(ResourceList, '/resource')

if __name__ == '__main__':

    # Instantiate database
    host = 'postgres'
    user = 'postgres'
    db_helper = DatabaseHelper(host, user, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    # Load API keys
    api_keys = None
    with open('api_keys.json') as json_file:
        api_keys = json.load(json_file)
    if api_keys is None:
        raise IOError("API key file 'api_keys.json' not found")

    # Resources without database backend (route APIs)
    news_api = NewsAPIResource('news', 'https://newsapi.org/v1/articles', 'apiKey', api_keys["NEWS_API_KEY"])
    nondb_resource_dict['news'] = news_api

    # Run micro server
    app.run(debug=True, host="0.0.0.0", port=8000)
    #app.run(debug=True, host="localhost", port=8000)

