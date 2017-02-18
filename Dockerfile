#
# example Dockerfile for https://docs.docker.com/examples/postgresql_service/
#

FROM ubuntu:latest

# Add the PostgreSQL PGP key to verify their Debian packages.
# RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository. It contains the most recent stable release
# RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Install postgres 9.5 (need postgreSQL >= 9.5 for insert on conflict feature)
RUN apt-get update && apt-get install -y python-pip postgresql-9.5 postgresql-client-9.5 postgresql-contrib-9.5 libpq-dev

# Upgrade pip
RUN pip install --upgrade pip


# Install necessary python packages
# psycopg2: postgreSQL library
# flask-restful: restful library for flask
RUN pip install psycopg2 flask-restful

# Copy over files
RUN mkdir /app
ADD run.sh ESGT_database_interface.py ESGT_restful_server.py /app/
WORKDIR /app
RUN chmod +x run.sh

# Run the rest of the commands as the ``postgres`` user created by the ``postgres-9.5`` package when it was ``apt-get installed``
USER postgres

# Create a PostgreSQL role named ``docker`` with ``docker`` as the password and
# then create a database `docker` owned by the ``docker`` role.
# Note: here we use ``&&\`` to run commands one after the other - the ``\``
#       allows the RUN command to span multiple lines.
RUN /etc/init.d/postgresql start
    #&&\
    #psql --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';" &&\
       # createdb -O docker docker

# Adjust PostgreSQL configuration
RUN echo "host all  all    127.0.0.1/32  trust" >> /etc/postgresql/9.5/main/pg_hba.conf
RUN echo "host all  all    ::1/128       trust" >> /etc/postgresql/9.5/main/pg_hba.conf
#RUN cat /etc/postgresql/9.5/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/9.5/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.5/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Set the default command to run when starting the container
#CMD ["/usr/lib/postgresql/9.5/bin/postgres", "-D", "/var/lib/postgresql/9.5/main", "-c", "config_file=/etc/postgresql/9.5/main/postgresql.conf"]

ENTRYPOINT ["/app/run.sh"]


