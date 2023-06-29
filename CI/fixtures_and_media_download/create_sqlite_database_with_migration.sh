#!/bin/bash

set -e -o xtrace

git checkout master

rm db.sqlite3 || true
python3 manage.py migrate

rm *.json* || true
wget -r --no-parent -nd https://dev.sfucsss.org/website/fixtures/ -A 'json'

python3 manage.py loaddata *.json
rm *.json* || true

git checkout -
