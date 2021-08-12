#!/bin/bash

set -e -o xtrace

function switch_nginx_to_construction_page {
  sudo rm /etc/nginx/sites-enabled/website
  sudo ln -s /etc/nginx/sites-available/construction /etc/nginx/sites-enabled/website
  sudo systemctl restart nginx.service
}



function go_to_root_directory {
  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  cd "${BASE_DIR}"
}

function install_latest_python_requirements {
  rm -fr "${BASE_DIR}/envCSSS"
  python3 -m virtualenv envCSSS
  . "${BASE_DIR}/envCSSS/bin/activate"
  python3 -m pip install -r "${BASE_DIR}/requirements.txt"
}

function create_directory_for_website_logs {
  mkdir -p "${BASE_DIR}/website_logs/python_logs/backup_script"
  mkdir -p "${BASE_DIR}/website_logs/python_logs/django_admin"
  mkdir -p "${BASE_DIR}/website_logs/python_logs/jenkins"
  mkdir -p "${BASE_DIR}/website_logs/python_logs/process_announcements"
  mkdir -p "${BASE_DIR}/website_logs/python_logs/update_officer_pics"
  mkdir -p "${BASE_DIR}/website_logs/python_logs/validate_resource_permissions"
  mkdir -p "${BASE_DIR}/website_logs/python_logs/create_fixtures"
  mkdir -p "${BASE_DIR}/website_logs/gunicorn_logs"
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
  export DB_CONTAINER_NAME="csss_site_db"
  docker run --name "${DB_CONTAINER_NAME}" -p "${DB_PORT}":5432 -it -d -e POSTGRES_PASSWORD="${DB_PASSWORD}" postgres:alpine || true
  wait_for_postgres_db
  docker exec "${DB_CONTAINER_NAME}" psql -U postgres -d postgres -c "CREATE DATABASE \"${DB_NAME}\" OWNER postgres;" || true
}

function applying_latest_db_migrations {
  chmod +x set_env.sh
  . ./set_env.sh site_envs/site_envs_jenkins

  setup_website_db

  cd "${BASE_DIR}/csss-site"
  python3 manage.py migrate
}

function update_static_files_location {
  # copying static files under their root directory
  python3 manage.py collectstatic --noinput

  # removing the static files that are under the source directory
  find "${BASE_DIR}/csss-site" -mindepth 1 -name 'static' -exec rm -rv {} +
}

function set_gunicorn_files {
  sudo systemctl daemon-reload
}

function updating_gunincorn {
  gunicorn_socket="gunicorn.socket"
  gunicorn="gunicorn.service"
  sudo systemctl restart "${gunicorn_socket}"
  sudo systemctl enable "${gunicorn_socket}"
  sudo systemctl status "${gunicorn_socket}"
  file "${socket_file_location}"
  sudo journalctl -u "${gunicorn_socket}"

  sudo systemctl restart "${gunicorn}"
  sudo systemctl enable "${gunicorn}"
  sudo systemctl status "${gunicorn}"
}

function update_nginx_configuration {
  sudo systemctl restart nginx.service
}

function clean_up_after_deployment {
  rm "/home/csss/deploy_changes.sh"
}

function switch_nginx_back_to_website {
  sudo rm /etc/nginx/sites-enabled/website
  sudo ln -s /etc/nginx/sites-available/website /etc/nginx/sites-enabled/website
  sudo systemctl restart nginx.service
}

switch_nginx_to_construction_page
go_to_root_directory
install_latest_python_requirements
create_directory_for_website_logs
applying_latest_db_migrations
update_static_files_location
set_gunicorn_files
updating_gunincorn
update_nginx_configuration
clean_up_after_deployment
switch_nginx_back_to_website