#!/bin/bash

set -e -o xtrace

function install_latest_python_requirements {
  . ~/envCSSS/bin/activate
  cd ~/csss-site
  python3.8 -m pip install -r requirements.txt
}

function setup_website_db {
  docker run --name csss_site_db -p "${DB_PORT}":5432 -it -d -e POSTGRES_PASSWORD="${DB_PASSWORD}" postgres:alpine || true
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
