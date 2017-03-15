#GATECH 2017 Spring Senior Design Project

## Setting up:

1. Install [Docker] (https://www.docker.com/).

2. `cd` into project root directory.

3. Run `docker-compose build` to build the docker container images.

3. Run `docker-compose run app /usr/local/bin/python setup.py --rm` to build the initial database.
    * To start with a fresh database, run the following:
        * `docker-compose run app /usr/local/bin/python setup.py clean --rm`
4. Run `docker-compose up -d` to launch containers as background daemons.

5. Access RESTful api on localhost, port 8000.
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
6. For Google authorization, go to http://127.0.0.1:8000/googlelogin
    * Input username and password information, and accept the access
    * Now go to http://127.0.0.1/resource/gmail for list of emails in inbox
#TODO: Instructions for google API creation with secret key

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

