#!/bin/bash

set -e -o xtrace

git checkout migration_CI

docker stop csss_website_db || true
docker rm csss_website_db || true
export DB_CONTAINER_NAME="csss_site_db_dev"
docker run --name ${DB_CONTAINER_NAME} -p ${DB_PORT}:5432 -it -d -e POSTGRES_PASSWORD=${DB_PASSWORD} postgres:alpine
sleep 5
docker exec "${DB_CONTAINER_NAME}" psql -U postgres -d postgres -c "CREATE DATABASE \"${DB_NAME}\" OWNER postgres;" || true

python3 manage.py migrate
python3 manage.py loaddata ../../migrations/fixtures/*
git checkout -