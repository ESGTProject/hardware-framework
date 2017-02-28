#GATECH 2017 Spring Senior Design Project

## Setting up:

1. Install [Docker] (https://www.docker.com/).

2. `cd` into project root directory.

3. Run `docker-compose build` to build the docker container images.

3. Run `docker-compose run app /usr/local/bin/python setup.py --rm` to build the initial database.

4. Run `docker-compose up -d` to launch containers as background daemons.

5. Access RESTful api on localhost, port 8000.
   Sample database endpoints:
   * [Light Sensor] (http://127.0.0.1:8000/light_sensor)

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

