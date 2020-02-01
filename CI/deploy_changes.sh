#!/bin/bash

set -e -o xtrace

. ~/envCSSS/bin/activate
cd ~/csss-site
python3.7 -m pip install -r requirements.txt
cd csss-site/src

chmod +x ~/setEnv.sh
. ~/setEnv.sh site_envs

docker run --name csss_site_db -p ${DB_PORT}:5432 -it -d -e POSTGRES_PASSWORD=${DB_PASSWORD} postgres:alpine || true

mkdir -p ~/csss-site/csss-site/src/logs

python3.7 manage.py migrate
python3.7 manage.py makemigrations
python3.7 manage.py migrate
python3.7 manage.py makemigrations 750_project
python3.7 manage.py migrate

python3.7 manage.py makemigrations about
python3.7 manage.py migrate

python3.7 manage.py makemigrations administration
python3.7 manage.py migrate

python3.7 manage.py makemigrations announcements
python3.7 manage.py migrate

python3.7 manage.py makemigrations bursaries_and_awards
python3.7 manage.py migrate

python3.7 manage.py makemigrations comp_sci_guide
python3.7 manage.py migrate

python3.7 manage.py makemigrations documents
python3.7 manage.py migrate

python3.7 manage.py makemigrations elections
python3.7 manage.py migrate

python3.7 manage.py makemigrations events
python3.7 manage.py migrate

python3.7 manage.py makemigrations file_uploads
python3.7 manage.py migrate

python3.7 manage.py collectstatic

sudo systemctl restart gunicorn.service

sudo systemctl status gunicorn.service
