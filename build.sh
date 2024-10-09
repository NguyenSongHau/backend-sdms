#!/usr/bin/env bash

pip install -r requirment.txt

python manage.py makemigrations --noinput

python manage.py migrate

python manage.py collectstatic --noinput --clear