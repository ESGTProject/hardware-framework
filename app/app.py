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
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import HttpAccessTokenRefreshError

import ESGT_database
from ESGT_database.database import DatabaseHelper

from ESGT_data import gmail  # TODO: Cache in database?


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
    def __init__(self, name, endpoint, api_key_query, api_key):
        self.name = name
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
            print ("Error retrieving data for {} at {}".format(
                self.name, self.endpoint))
            return jsonify(None)


class GmailAPIResource(object):
    def __init__(self):
        self.gmail_client = gmail.Gmail()

    def get(self, params={}):
        params = params.to_dict()
        store = Storage(CREDENTIAL_PATH)
        credentials = store.get()
        try:
            if credentials is None or credentials.invalid or credentials.access_token_expired:
                return "Invalid Credential or Token Timeout"
            else:
                limit = DEFAULT_RESOURCE_LENGTH
                if 'limit' in params:
                    limit = int(params['limit'])
                    del params['limit']
                mail_list = self.gmail_client.get_json(credentials)
                mail_list = mail_list if len(
                    mail_list) <= limit else mail_list[:limit]
                return jsonify(mail_list)
        except HttpAccessTokenRefreshError as e:
            return "Invalid Token"

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
        # flask.session['credentials'] = credentials.to_json()
        store = Storage(CREDENTIAL_PATH)
        store.put(credentials)
        return flask.redirect(flask.url_for('resource/gmail'))


# POST receiver for mobile application that sends authentication code
@app.route('/googleauth', methods=['GET', 'POST'])
def googleauth():
    if request.method == 'POST':
        # Exchange auth code for access token, refresh token, and ID token
        auth_code = request.form['auth_code']
        credentials = client.credentials_from_clientsecrets_and_code(
            filename=CLIENT_SECRET_FILE,
            scope=['https://www.googleapis.com/auth/gmail.readonly',
                   'profile', 'email'],
            code=auth_code,
            redirect_uri=flask.url_for('googlecallback', _external=True))
        store = Storage(CREDENTIAL_PATH)
        store.put(credentials)
        return auth_code
    elif request.method == 'GET':
        store = Storage(CREDENTIAL_PATH)
        credentials = store.get()
        userid = credentials.id_token['sub']
        email = credentials.id_token['email']
        return userid + " " + email
    else:
        return None


# Configuration endpoint TODO: Authentication of user
@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            post_args = request.json
            user = post_args['username']
            config = post_args['config']
            refresh_tokens = post_args['refresh_tokens']
            if user is not None and config is not None and refresh_tokens is not None:
                db_helper.insert_config(user, config, refresh_tokens)
                return 'config POST success'
        else:
            return 'config POST failure'
    elif request.method == 'GET':
        user = request.args.get('username')
        if user is not None:
            row = db_helper.select_config(user)
            return jsonify(row)
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

    # Create credential path
    if not os.path.exists(os.path.dirname(CREDENTIAL_PATH)):
        os.makedirs(os.path.dirname(CREDENTIAL_PATH))

    # Resources without database backend (route APIs)
    news_api = NewsAPIResource(
        'news', 'https://newsapi.org/v1/articles', 'apiKey', api_keys["NEWS_API_KEY"])
    gmail_api = GmailAPIResource()
    nondb_resource_dict['news'] = news_api
    nondb_resource_dict['gmail'] = gmail_api

    # Run micro server
    app.run(debug=True, host="0.0.0.0", port=8000)
    #app.run(debug=True, host="localhost", port=8000)
