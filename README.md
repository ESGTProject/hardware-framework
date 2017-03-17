#GATECH 2017 Spring Senior Design Project

## Setting up:

1. Install [Docker] (https://www.docker.com/).

2. `cd` into project root directory.

3. Run `docker-compose build` to build the docker container images.

3. Run `docker-compose run app /usr/local/bin/python setup.py --rm` to build the initial database.
    * To start with a fresh database, run the following:
        * `docker-compose run app /usr/local/bin/python setup.py clean --rm`
4. Run `docker-compose up -d` to launch containers as background daemons.

## API

1. Config endpoints (requires Android App)
    Get configuration per user
    * `http://127.0.0.1:8000/config`

    Parameters:
    * `?username=<username>` email of user (REQUIRED)
    * example: `http://127.0.0.1:8000/config?username=myemail@gmail.com

2. Resource endpoints
    Get list of resource endpoints:
    * `http://127.0.0.1:8000/resource`
    * [Resources] (http://127.0.0.1:8000/resource)

    Then access the resource:
    * `http://127.0.0.1:8000/resource/<resource_name>`

    Example:
    * `http://127.0.0.1:8000/resouce/weather`

    Supported parameters:
    * `?limit=<num>` Limits the number of results returned
    * `?source=<news source>` For `/resource/news` endpoint only, (REQUIRED)
        - [List of sources] (https://newsapi.org/sources)
        - example: `http://127.0.0.1:8000/resource/news?source=google-news`

    Gmail support (requires Android App):
    * Gmail requires authorization to access Gmail services via OAuth
    * The Android Application allows users to send OAuth tokens to the backend server
    * After successful authorization, the API endpoint to access is at (replace USERNAME with email)
        - `http://127.0.0.1:8000/resource/gmail?username=USERNAME

3. For Gmail support, follow the steps below
    * Log into the [Google API console] (https://console.developers.google.com)
    * Create a new project if one does not exist (Name it whatever you wish)
    * Click on Credentials in the left pane
    * Click on the "Create credentials" button and select "OAuth client ID"
    * Choose "Web application" for application type
        * Name it whatever you wish
        * Add the following to authorized JavaScript origins (using your domain name)
            - http://127.0.0.1:8000
            - http://your-domain-name:8000
        * Add the following to the authorized redirect URIs (Note that this is for DEPRECATED feature of logging in through web!)
            - http://127.0.0.1:8000/googlecallback
            - http://your-domain-name:8000/googlecallback
    * Click create to finish
    * Click on the download icon in the far right to download the client secret json
    * Rename the secret to "gmail_client_secret.json" and put it in /app directory of the project folder

DEPRECATED (This is left for development purposes)
1. For Google authorization, go to http://127.0.0.1:8000/googlelogin
    * Input username and password information, and accept the access
    * Now go to http://127.0.0.1/resource/gmail for list of emails in inbox

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
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
```

