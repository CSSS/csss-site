#!/bin/bash

set -e -o xtrace

git checkout master

rm sqlite || true
python3 manage.py migrate

pushed ../../fixtures/
rm *.json* || true
wget -r --no-parent -nd https://dev.sfucsss.org/fixtures/ -A 'json'
popd

python3 manage.py loaddata ../../fixtures/*

git checkout -
