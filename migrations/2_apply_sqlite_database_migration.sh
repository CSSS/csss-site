#!/bin/bash

set -e -o xtrace

git checkout master

rm sqlite || true
python3 manage.py migrate
python3 manage.py loaddata ../../migrations/fixtures/*

git checkout -