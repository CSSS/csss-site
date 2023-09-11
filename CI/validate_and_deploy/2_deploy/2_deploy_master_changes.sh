#!/bin/bash

set -e -o xtrace

function go_to_root_directory {
  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  cd "${BASE_DIR}"
}

function open_source_code_zip_folder() {
    tar xvf csss-site-source-code.tar.gz
    rm csss-site-source-code.tar.gz
}

function install_latest_python_requirements {
  rm -fr "${BASE_DIR}/envCSSS"
  python3 -m virtualenv envCSSS
  . "${BASE_DIR}/envCSSS/bin/activate"
  python3 -m pip install -r "${BASE_DIR}/requirements.txt"
}

function create_directory_for_website_logs {
  mkdir -p "${BASE_DIR}/website_logs/gunicorn_logs"
  mkdir -p "${BASE_DIR}/website_logs/backup_script"
  mkdir -p "${BASE_DIR}/website_logs/create_fixtures"
  mkdir -p "${BASE_DIR}/website_logs/django_admin"
  mkdir -p "${BASE_DIR}/website_logs/jenkins"
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
  . ./set_env.sh csss_site_envs/csss_site_jenkins.env

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
  sleep 10
  sudo systemctl status "${gunicorn_socket}"
  file "${socket_file_location}"
  sudo journalctl -u "${gunicorn_socket}"

  sudo systemctl restart "${gunicorn}"
  sleep 10
  sudo systemctl status "${gunicorn}"
}

function update_nginx_configuration {
  nginx_service="nginx.service"
  sudo systemctl restart "${nginx_service}"
  sleep 10
  sudo systemctl status "${nginx_service}"
}

function restart_cron_job_service {
  csss_website_cron_job="cron.service"
  sudo systemctl restart "${csss_website_cron_job}"
  sleep 10
  sudo systemctl status "${csss_website_cron_job}"
}


function restart_error_reporting_service {
  csss_website_error_reporting="error_reporting.service"
  sudo systemctl restart "${csss_website_error_reporting}"
  sleep 10
  sudo systemctl status "${csss_website_error_reporting}"
}

function clean_up_after_deployment {
  rm "/home/csss/deploy_changes.sh"
  rm -r "${LOG_LOCATION}"
}



go_to_root_directory
open_source_code_zip_folder
install_latest_python_requirements
create_directory_for_website_logs
applying_latest_db_migrations
update_static_files_location
set_gunicorn_files
updating_gunincorn
update_nginx_configuration
restart_cron_job_service
restart_error_reporting_service
clean_up_after_deployment
