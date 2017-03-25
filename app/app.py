#!/usr/bin/python

'''
File name: app.py
Author: Kairi Kozuma
Date created: 02/16/2017
Date last modified: 03/15/2017
Python Version: 2.7.11
'''
import flask
from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from flask_cors import CORS, cross_origin
import sqlalchemy
import json
import pytz
import os
from datetime import datetime
import requests
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import HttpAccessTokenRefreshError

import ESGT_database
from ESGT_database.database import DatabaseHelper

from ESGT_data import gmail
from ESGT_data import open_weather_map
# TODO: Cache in database?


class ISODatetimeEncoder(JSONEncoder):
    """Custom ISO format for json encoding of datetime objects"""

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
        except TypeError:
            pass
        return JSONEncoder.default(self, obj)


# Set up flask app variables
app = Flask(__name__)
app.json_encoder = ISODatetimeEncoder
CORS(app)  # Enable CORS

# Default number of items to return
DEFAULT_RESOURCE_LENGTH = 10

# Database helper for backend postgresql
db_helper = None

# Non database helper for other (non database backed up) resources
nondb_resource_dict = {}

CLIENT_SECRET_FILE = 'gmail_client_secret.json'
CREDENTIAL_PATH = './.credentials/gmail-session.json'


def flatten(row):
    """Adds timestamp to same row as json object stored in row.value

    Arguments:
        row : Row returned from query into database
            row.val is the json object
            row.time_created is the time stamp

    Returns:
        Dictionary with the timestamp flattened into the json object at row.value
    """
    dct = json.loads(row.value)
    dct["timestamp"] = pytz.utc.localize(
        row.time_created, is_dst=None).astimezone(pytz.utc)
    return dct


class NewsAPIResource(object):
    def __init__(self, endpoint, api_key_query, api_key):
        self.endpoint = endpoint
        self.api_key_query = api_key_query
        self.api_key = api_key

    def get(self, params={}):
        params = params.to_dict()
        # Extract limit if there is one
        limit = DEFAULT_RESOURCE_LENGTH
        if 'limit' in params:
            limit = int(params['limit'])
            del params['limit']
        # Add api key to parameter
        params[self.api_key_query] = self.api_key  # add api key to params
        try:
            r = requests.get(self.endpoint, params)
            articles = r.json()['articles']
            articles = articles if len(articles) <= limit else articles[:limit]
            return jsonify(articles)
        except:
            print ("NewsAPI Error:{}".format(self.endpoint))
            return jsonify(None)


class GmailAPIResource(object):
    def __init__(self):
        self.gmail_client = gmail.Gmail()

    def get(self, params={}):
        # Get credentials from username
        if "username" not in params:
            return "required parameter 'username' missing"
        username = params["username"]
        credentials = get_stored_credentials(username)
        # Refresh token if expired
        if credentials.access_token_expired:
            credentials.refresh(httplib2.Http())
            store_credentials(username, credentials)

        # Use limit to limit output
        params = params.to_dict()
        limit = DEFAULT_RESOURCE_LENGTH
        if 'limit' in params:
            limit = int(params['limit'])
            del params['limit']

        # Attempt to get gmail inbox
        try:
            if credentials is None or credentials.invalid:
                return "Invalid Credential or Token Timeout"
            else:
                mail_list = self.gmail_client.get_json(credentials)
                mail_list = mail_list if len(mail_list) <= limit else mail_list[:limit]
                return jsonify(mail_list)
        except HttpAccessTokenRefreshError as e:
            return "Invalid Token"

class WeatherAPIResource(object):
    def __init__(self, api_key):
        self.weather_client = open_weather_map.OpenWeatherMap(api_key)

    def get(self, params={}):
        # Get required location parameter
        if "location" not in params:
            return "required parameter 'location' missing"
        location = params["location"]

        # Use limit to limit output
        params = params.to_dict()
        limit = DEFAULT_RESOURCE_LENGTH
        if 'limit' in params:
            limit = int(params['limit'])
            del params['limit']

        weather_json = json.loads(self.weather_client.get_json(location));
        return jsonify(weather_json)

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
APPLICATION_NAME = 'ESGT Backend'

# Deprecated (for debugging only)
@app.route('/googlelogin')
def googlelogin():
    # Attempt new login
    return flask.redirect(flask.url_for('googlecallback'))


# Deprecated (for debugging only)
@app.route('/googlecallback')
def googlecallback():
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope=SCOPES,
        redirect_uri=flask.url_for('googlecallback', _external=True))
    flow.params['access_type'] = 'offline'
    flow.params['include_granted_scopes'] = 'true'
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        return flask.redirect(flask.url_for('resource/gmail', _external=True))


# POST receiver for mobile application that sends authentication code
@app.route('/googleauth', methods=['GET', 'POST'])
def googleauth():
    if request.method == 'POST':
        print ('Received', request.json)
        username = request.json['username']
        auth_code = request.json['auth_code']
        # Exchange auth code for access token, refresh token, and ID token
        credentials = client.credentials_from_clientsecrets_and_code(
            filename=CLIENT_SECRET_FILE,
            scope=['https://www.googleapis.com/auth/gmail.readonly',
                   'profile', 'email'],
            code=auth_code,
            redirect_uri=flask.url_for('googlecallback', _external=True))
        store_credentials(username, credentials)
        return "successful login"
    elif request.method == 'GET':
        print ('Received', request.json)
        user = request.json['username']
        credentials = get_stored_credentials(user)
        if credentials is None:
            email = credentials.id_token['email']
            return email
        else:
            return 'No valid token'
    else:
        return None


# Helper method to get stored credentials (token)
def get_stored_credentials(username):
    row = db_helper.select_credentials(username)
    try:
        print (row[0][0])
        json = row[0][0]
        return client.Credentials.new_from_json(json)
    except IndexError as e:
        return None


# Helper method to store credentials in database (token)
def store_credentials(username, credentials):
    json = credentials.to_json();
    row = db_helper.insert_credentials(username, json)


# Configuration endpoint TODO: Authentication of user
@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        print ('Received', request.json)
        user = request.json['username']
        config = request.json['config']
        if user is not None and config is not None:
            db_helper.insert_config(user, config)
            return 'config POST success'
        else:
            return 'config POST failure'
    elif request.method == 'GET':
        user = request.args.get('username')
        if user is not None:
            row = db_helper.select_config(user)
            return jsonify(row[0])
        else:
            return 'config GET failure'
    else:
        return 'Invalid config request'


# Resource API endpoint
@app.route('/resource/<string:resource>', methods=['GET'])
def get_resource(resource):
    # If it is a nondatabase resource, call the object's get function
    if resource in nondb_resource_dict:
        args = request.args
        return nondb_resource_dict[resource].get(args)
    # Use database to build response
    else:
        limit_str = request.args.get('limit')
        limit = int(
            limit_str) if limit_str is not None else DEFAULT_RESOURCE_LENGTH
        rows = db_helper.select(resource, limit)
        if rows is not None:
            elem_array = list(map(flatten, rows))
            return jsonify(elem_array)


# Resource list API endpoint
@app.route('/resource', methods=['GET'])
def get_resource_list():
    # List of resources from database
    list_of_lists = db_helper.select_resources()
    # Flatten list of lists
    resource_list = [v for sublist in list_of_lists for v in sublist]
    # Add list of resources from non database resources
    resource_list.extend(nondb_resource_dict.keys())
    return jsonify(resource_list)


if __name__ == '__main__':
    # Instantiate database
    config = None
    with open('config.json') as json_file:
        config = json.load(json_file)
    if config is None:
        raise IOError("Configuration file 'config.json' not found")
    user = config['user']
    password = config['password']
    host = config['host']
    db_helper = DatabaseHelper(user, password, host, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    # Create credential path
    if not os.path.exists(os.path.dirname(CREDENTIAL_PATH)):
        os.makedirs(os.path.dirname(CREDENTIAL_PATH))

    # Resources without database backend (route APIs)
    news_api = NewsAPIResource('https://newsapi.org/v1/articles', 'apiKey', config["NEWS_API_KEY"])
    gmail_api = GmailAPIResource()
    weather_api = WeatherAPIResource(config["OWM_API_KEY"])

    nondb_resource_dict['news'] = news_api
    nondb_resource_dict['gmail'] = gmail_api
    nondb_resource_dict['weather'] = weather_api

    # Run micro server
    app.run(debug=True, host="0.0.0.0", port=8000)
