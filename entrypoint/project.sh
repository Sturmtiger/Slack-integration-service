#!/bin/bash

HOST=0.0.0.0
PORT=7777

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata data.json
python3 manage.py runserver "$HOST":"$PORT"
