#!/usr/bin/python

'''
File name: app.py
Author: Kairi Kozuma
Date created: 02/16/2017
Date last modified: 03/29/2017
Python Version: 3.6.0
'''
import flask
from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from flask_cors import CORS, cross_origin
import sqlalchemy
import json
import pytz
import os
import pyrebase
import requests
import httplib2
from datetime import datetime
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import HttpAccessTokenRefreshError

import ESGT_database
from ESGT_database.database import DatabaseHelper

from ESGT_data import gmail
from ESGT_data import google_calendar
from ESGT_data import open_weather_map

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

# Firebase global instance
firebase = None

# Device UUID
device_uid = None

CLIENT_SECRET_FILE = 'gmail_client_secret.json'

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


class GoogleAPIResource(object):
    def __init__(self):
        self.credentials = None

    def check_credentials(self, user_uid):
        google_token_db = "google"

        # If length is less than 60, auth code given
        # Convert auth code to credential
        cred = firebase.database().child("users").child(user_uid).child("tokens").child(google_token_db).get().val()
        if (len(cred) < 60):
            credentials = client.credentials_from_clientsecrets_and_code(
            filename=CLIENT_SECRET_FILE,
            scope=['https://www.googleapis.com/auth/gmail.readonly'],
            code=cred,
            redirect_uri=flask.url_for('oauthhandler', _external=True))
            print (credentials.to_json())
            firebase.database().child("users").child(user_uid).child("tokens").update({google_token_db:credentials.to_json()})
        else:
            # Create credentials from credentials json
            credentials = client.Credentials.new_from_json(json.loads(json.dumps(cred)))

        # Refresh token if expired
        if credentials.access_token_expired:
            credentials.refresh(httplib2.Http())
            firebase.database().child("users").child(user_uid).child("tokens").update({google_token_db:credentials.to_json()})

        self.credentials = credentials


class GmailAPIResource(GoogleAPIResource):
    def __init__(self):
        self.gmail_client = gmail.Gmail()

    def get(self, params={}):
        # Get credentials
        if "user_uid" not in params:
            return "required parameter 'user_uid' missing"
        user_uid = params["user_uid"]
        # Check credentials
        self.check_credentials(user_uid)

        # Use limit to limit output
        params = params.to_dict()
        limit = DEFAULT_RESOURCE_LENGTH
        if 'limit' in params:
            limit = int(params['limit'])
            del params['limit']

         # Attempt to get gmail inbox
        try:
            if self.credentials is None or self.credentials.invalid:
                return "Invalid Credential or Token Timeout"
            else:
                mail_list = self.gmail_client.get_json(self.credentials)
                if mail_list is not None:
                    mail_list = mail_list if len(mail_list) <= limit else mail_list[:limit]
                    return jsonify(mail_list)
                else:
                    return "No emails"

        except HttpAccessTokenRefreshError as e:
            return "Invalid Token"

class GoogleCalendarAPIResource(GoogleAPIResource):
    def __init__(self):
        self.google_calendar_client = google_calendar.GoogleCalendar()

    def get(self, params={}):
        # Get credentials
        if "user_uid" not in params:
            return "required parameter 'user_uid' missing"
        user_uid = params["user_uid"]
        # Check credentials
        self.check_credentials(user_uid)

        # Use limit to limit output
        params = params.to_dict()
        limit = DEFAULT_RESOURCE_LENGTH
        if 'limit' in params:
            limit = int(params['limit'])
            del params['limit']

         # Attempt to get gmail inbox
        try:
            if self.credentials is None or self.credentials.invalid:
                return "Invalid Credential or Token Timeout"
            else:
                event_list = self.google_calendar_client.get_json(self.credentials)
                if event_list is not None:
                    event_list = event_list if len(event_list) <= limit else event_list[:limit]
                    return jsonify(event_list)
                else:
                    return "No events"
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

# Deprecated (for debugging only)
@app.route('/oauthhandler')
def oauthhandler():
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

# Configuration endpoint TODO: Authentication of user
@app.route('/uid', methods=['GET'])
def config():
    if request.method == 'GET':
        return jsonify(device_uid)


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
    device_uid = None
    with open('config.json') as json_file:
        config = json.load(json_file)
    if config is None:
        raise IOError("Configuration file 'config.json' not found")
    user = config['database']['user']
    password = config['database']['password']
    host = config['database']['host']
    db_helper = DatabaseHelper(user, password, host, ESGT_database.database.DB_ESGT)
    db_helper.connect()

    # Resources without database backend (route APIs)
    news_api = NewsAPIResource('https://newsapi.org/v1/articles', 'apiKey', config["NEWS_API_KEY"])
    gmail_api = GmailAPIResource()
    calendar_api = GoogleCalendarAPIResource()
    weather_api = WeatherAPIResource(config["OWM_API_KEY"])

    nondb_resource_dict['news'] = news_api
    nondb_resource_dict['gmail'] = gmail_api
    nondb_resource_dict['calendar'] = calendar_api
    nondb_resource_dict['weather'] = weather_api

    # Setup firebase database
    firebase = pyrebase.initialize_app(config['firebase'])
    firebase_db = firebase.database();

    # Device config to send to Firebase
    config_device = {}
    config_device['serial_number'] = "SERIALNUMBERTEMP"
    config_device['user_current'] = ''

    # Get unique ID for device (if not present in config, or if id is not present in firebase)
    device_list = firebase_db.child("devices").get().val()
    print (device_list)
    if ('device_uid' not in config) or (device_list is None) or (config['device_uid'] not in device_list):
        device = firebase_db.child('devices').push(config_device)
        config['device_uid'] = device['name']
        # Write updated config json to file
        with open('config.json', 'w') as json_file:
            json.dump(config, json_file)

    # Set global uuid variable
    device_uid = config['device_uid']

    # Run micro server
    app.run(debug=True, host="0.0.0.0", port=8000, threaded=True)
