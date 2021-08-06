#!/bin/bash

set -e -o xtrace

git checkout master

rm sqlite || true
python3 manage.py migrate
wget -r --no-parent -nd https://dev.sfucsss.org/fixtures/
python3 manage.py loaddata ../../migrations/*

git checkout -
