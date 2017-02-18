#!/bin/bash
#usr/lib/postgresql/9.5/bin/postgres -D /var/lib/postgresql/9.5/main -c config_file=/etc/postgresql/9.5/main/postgresql.conf
# Run postgres and python server

/etc/init.d/postgresql start & python ESGT_restful_server.py
