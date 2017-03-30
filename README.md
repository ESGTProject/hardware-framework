#GATECH 2017 Spring Senior Design Project

## Setup (TODO)

## API (replace <host> with actual host)
1. Resource endpoints
    Get list of resource endpoints:
    * `http://<host>:8000/resource`
    * [Resources] (http://<host>:8000/resource)

    Then access the resource:
    * `http://<host>:8000/resource/<resource_name>`

    Parameters:
    * `?limit=<num>` Limits the number of results returned

    NewsAPI:
    * `?source=<news source>` For `/resource/news` endpoint only (REQUIRED)
        - [List of sources] (https://newsapi.org/sources)
        - example: `http://<host>:8000/resource/news?source=google-news`

    WeatherAPI:
    * `?location=<city id>` For `/resource/weather` endpoint only (REQUIRED)
        - [List of city IDs] (http://openweathermap.org/help/city_list.txt)
        - example: `http://<host>:8000/resource/news?location=4180439`

    GmailAPI (requires Android App):
    * Gmail requires authorization to access Gmail services via OAuth
    * The Android Application allows users to send OAuth tokens to the backend server
    * After successful authorization, the API endpoint to access is at
        - `http://<host>:8000/resource/gmail?user_uid=<user_uid>`
    * `?user_uid=<user_uid>` For `/resource/gmail` endpoint (REQUIRED)
        - `user_uid` is the unique identifier for the current user

2. Unique ID
    Get the unique id (UID) for the device
    * `http://<host>:8000/uid`

3. For Gmail support, follow the steps below
    * Log into the [Google API console] (https://console.developers.google.com)
    * Create a new project if one does not exist (Name it whatever you wish)
    * Click on Credentials in the left pane
    * Click on the "Create credentials" button and select "OAuth client ID"
    * Choose "Web application" for application type
        * Name it whatever you wish
        * Add the following to authorized JavaScript origins (using your domain name)
            - http://<host>:8000
            - http://your-domain-name:8000
        * Add the following to the authorized redirect URIs (Note that this is for DEPRECATED feature of logging in through web!)
            - http://<host>:8000/oauthhandler
            - http://your-domain-name:8000/oauthhandler
    * Click create to finish
    * Click on the download icon in the far right to download the client secret json
    * Rename the secret to "gmail_client_secret.json" and put it in /app directory of the project folder


## Setting up with Docker (DEPRECATED, not updated for Python 3.6.0):

1. Install [Docker] (https://www.docker.com/).

2. `cd` into project root directory.

3. Run `docker-compose build` to build the docker container images.

3. Run `docker-compose run app /usr/local/bin/python setup.py --rm` to build the initial database.
    * To start with a fresh database, run the following:
        * `docker-compose run app /usr/local/bin/python setup.py clean --rm`
4. Run `docker-compose up -d` to launch containers as background daemons.

##Trouble shooting macOS
### 1. To install psycopg2, install postgresql first
`brew install postgresql`
`pip install psycopg2`

##Trouble shooting RPi 3
### 1. To run app/updater.py, use sudo
`sudo python app/updater.py`

This is necessary to access hardware.

### 2. Install postgreSQL 9.6 on Raspberry Pi

1. Add backports to sources
 - Add following line to `/etc/apt/sources.list.d/sources.list`

    `deb http://ftp.debian.org/debian jessie-backports main`

2. Run `sudo apt-get update`

3. Install postgresql 9.6

    `sudo apt-get -t jessie-backports install postgresql-9.6`

4. Change following line in `/etc/postgresql/9.6/main/pg_hba.conf`
```
local   all             all                                     trust
host    all             all             <host>/32            trust
host    all             all             ::1/128                 trust
```

