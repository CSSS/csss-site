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

cd csss-site/src

../../CI/migrate_apps.sh ./

python3.7 manage.py collectstatic --noinput

find /home/csss/csss-site/csss-site/src -mindepth 1 -regex '.*static.*' -delete

sudo systemctl restart gunicorn.service

sudo systemctl status gunicorn.service
