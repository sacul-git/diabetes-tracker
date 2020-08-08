#!/bin/sh
exec gunicorn --workers 1 -b 0.0.0.0:5017 --access-logfile - --error-logfile - index:server
