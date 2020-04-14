#!/bin/bash

set -e -o xtrace

function install_latest_python_requirements {
  python3.8 -m pip install virtualenv
  if [ -f envCSSS/bin/python ]; then
    virtualenv_python_version=$(./envCSSS/bin/python --version)
    if [ "${virtualenv_python_version}" != "Python 3.8.0" ]; then
      echo "the python version on the target server is not 3.8.0"
      echo "the system may act in unintended ways"
      echo "exiting now"
      exit 1
    fi
    . ~/envCSSS/bin/activate
  else
    python3.8 -m virtualenv envCSSS
    . ~/envCSSS/bin/activate
  fi

  cd ~/csss-site
  python3.8 -m pip install -r requirements.txt
}

function wait_for_postgres_db {
  # aquired from https://docs.docker.com/compose/startup-order/
  until PGPASSWORD=$DB_PASSWORD psql -h localhost -p "${DB_PORT}" -U "postgres" -c '\q'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
  done

  >&2 echo "Postgres is up"
}

function setup_website_db {
  docker run --name csss_site_db -p "${DB_PORT}":5432 -it -d -e POSTGRES_PASSWORD="${DB_PASSWORD}" postgres:alpine || true
  wait_for_postgres_db
}

function create_directory_for_website_logs {
  mkdir -p ~/csss-site/csss-site/src/logs
}

function applying_latest_db_migrations {
  chmod +x ~/set_env.sh
  . ~/set_env.sh site_envs

  setup_website_db

  cd csss-site/src
  chmod +x ~/migrate_apps.sh
  . ~/migrate_apps.sh || true
}

function update_static_files_location {
  # copying static files under their root directory
  python3.8 manage.py collectstatic --noinput

  # removing the static files that are under the source directory
  find /home/csss/csss-site/csss-site/src -mindepth 1 -regex '.*static.*' -delete
}

function updating_gunincorn {
  sudo systemctl restart gunicorn.service
  sudo systemctl status gunicorn.service
}

install_latest_python_requirements
create_directory_for_website_logs
applying_latest_db_migrations
update_static_files_location
updating_gunincorn
