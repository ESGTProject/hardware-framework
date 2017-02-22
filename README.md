
2017 Spring Senior Design

Configure the sensors to Rsp3 B.



#GATECH 2017 Spring Senior Design Project


##Trouble shooting on testing sripts for MacOS
### 1. To install psycopg2, install postgresql first
brew install postgresql

pip install psycopg2


##Trouble shooting on testing sripts for RSBP 3
### 1. To Run the script with serial cmd
add 'sudo' to promote the permission to drive the serial port 

Setting up:

1. Install [Docker] (https://www.docker.com/).
2. `cd` into project root directory.
3. Run `docker-compose build` to build the docker container images.
3. Run `docker-compose run app /usr/local/bin/python create_db.py --rm` to build the initial database.
4. Run `docker-compose up -d` to launch containers as background daemons.
5. Access RESTful api on localhost, port 8000.
   Sample database endpoints:
   * [Light Sensor] (http://127.0.0.1:8000/light_sensor)
   * [Temperature Sensor] (http://127.0.0.1:8000/temp_sensor)
   * [Proximity Sensor] (http://127.0.0.1:8000/proximity_sensor)
