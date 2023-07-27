#!/bin/bash

set -e -o xtrace

git checkout master


if [ -z "${DB_CONTAINER_NAME}" ]; then
	echo "DB_CONTAINER_NAME is not set, exiting."
	exit 1
fi

function setup_website_db {
  docker rm -f "${DB_CONTAINER_NAME}" || true
  docker run --name "${DB_CONTAINER_NAME}" -p "${DB_PORT}":5432 -it -d -e POSTGRES_PASSWORD="${DB_PASSWORD}" postgres:alpine || true
  wait_for_postgres_db
  docker exec "${DB_CONTAINER_NAME}" psql -U postgres -d postgres -c "CREATE DATABASE \"${DB_NAME}\" OWNER postgres;" || true
}

function wait_for_postgres_db {
  # aquired from https://docs.docker.com/compose/startup-order/
  until PGPASSWORD=$DB_PASSWORD psql -h localhost -p "${DB_PORT}" -U "postgres" -c '\q'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
  done

  >&2 echo "Postgres is up"
}

function applying_master_db_migrations {
  python3 manage.py migrate
  rm *.json* || true
  if [ -z "${CHANGE_ID}" ]; then
    if [ $(echo $USER) = "jace" ]; then
      ssh staging "grep -v 'redact' csss-site-fixtures-and-media-setup-for-staging/download_fixtures_and_media.sh  > csss-site-fixtures-and-media-setup-for-staging/live_download_fixtures_and_media.sh"
      ssh staging "cd ~/csss-site-fixtures-and-media-setup-for-staging/ && /home/csss/csss-site-fixtures-and-media-setup-for-staging/live_download_fixtures_and_media.sh"
    fi
    wget -r --no-parent -nd https://dev.sfucsss.org/website/fixtures/ -A 'json'
    if [ $(echo $USER) = "jace" ]; then
      ssh staging "cd ~/csss-site-fixtures-and-media-setup-for-staging/ && /home/csss/csss-site-fixtures-and-media-setup-for-staging/download_fixtures_and_media.sh"
    fi
  else
    cp /home/csss/staging_assets/website/fixtures/* .
  fi
  python3 manage.py loaddata *.json
  rm *.json* || true
}


setup_website_db
applying_master_db_migrations

git checkout -
