pip3 install -r requirements.txt
python3.12 manage.py collectstatic --noinput
python3.12 manage.py makemigrations --noinput
python3.12 manage.py migrate --noinput
python3.12 manage.py collectdata