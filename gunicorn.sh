#!/bin/sh
gunicorn wsgi:app \
    --log-file bakery-error.log \
    -p /var/www/bakery.pid -D \
    -w 4 \
    --worker-class socketio.sgunicorn.GeventSocketIOWorker \
    -b 0.0.0.0:5000
