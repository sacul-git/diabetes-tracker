#!/bin/sh
exec gunicorn --workers 1 --certfile cert.pem --keyfile key.pem -b 0.0.0.0:$FLASKPORT --access-logfile - --error-logfile - index:server
