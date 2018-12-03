#!/bin/bash

#python3 /code/manage.py flush --noinput
python3 /code/manage.py makemigrations
python3 /code/manage.py migrate --noinput
#python3 /code/import_data.py
python3 /code/manage.py runserver 0.0.0.0:8000
