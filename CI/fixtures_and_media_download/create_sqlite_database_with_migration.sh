#!/bin/bash

set -e -o xtrace

git checkout master

rm sqlite || true
python3 manage.py migrate

rm *.json* || true
wget -r --no-parent -nd https://dev.sfucsss.org/dev_csss_website_media/fixtures/ -A 'json'

python3 manage.py loaddata *.json
rm *.json* || true

git checkout -
