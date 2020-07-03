#!/bin/bash

HOST=0.0.0.0
PORT=7777

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata dump.json
python manage.py runserver "$HOST":"$PORT"
