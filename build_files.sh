#!/bin/bash

# Cài đặt các thư viện từ requirements.txt
pip install -r requirements.txt

# Chạy lệnh collectstatic
python manage.py collectstatic --noinput
