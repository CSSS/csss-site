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
	if [ -z "${CHANGE_ID}" ]; then
		if [ $(echo $USER) = "jace" ]; then
			ssh dev "grep -v 'redact' csss-fixtures-and-media-setup-for-staging/download_fixtures_and_media.sh  > csss-fixtures-and-media-setup-for-staging/live_download_fixtures_and_media.sh"
			ssh dev "cd ~/csss-fixtures-and-media-setup-for-staging/ && chmod +x live_download_fixtures_and_media.sh && ./live_download_fixtures_and_media.sh"
		fi
		rm csss_cron_info.json elections.json errors.json about.json resource_management.json || true
		wget https://dev.sfucsss.org/website/fixtures/csss_cron_info.json
		wget https://dev.sfucsss.org/website/fixtures/elections.json
		wget https://dev.sfucsss.org/website/fixtures/errors.json
		wget https://dev.sfucsss.org/website/fixtures/about.json
		wget https://dev.sfucsss.org/website/fixtures/resource_management.json
		if [ $(echo $USER) = "jace" ]; then
			ssh dev "cd ~/csss-fixtures-and-media-setup-for-staging/ && ./download_fixtures_and_media.sh"
		fi
		python3 manage.py loaddata csss_cron_info.json
		python3 manage.py loaddata elections.json
		python3 manage.py loaddata errors.json
		python3 manage.py loaddata about.json
		python3 manage.py loaddata resource_management.json
		rm csss_cron_info.json elections.json errors.json about.json resource_management.json
	else
		cp /home/csss/staging_assets/website/fixtures/* .
		python3 manage.py loaddata *.json
		rm *.json*
	fi
}


setup_website_db
applying_master_db_migrations

git checkout -
