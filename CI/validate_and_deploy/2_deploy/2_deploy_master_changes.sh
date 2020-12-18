#!/bin/bash

set -e -o xtrace

function go_to_root_directory {
  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  cd "${BASE_DIR}"
}

function install_latest_python_requirements {
  python3 -m pip install virtualenv
  if [ -f envCSSS/bin/python ]; then
    virtualenv_python_version=$(./envCSSS/bin/python --version)
    if [ "${virtualenv_python_version}" != "Python 3.8.0" ]; then
      echo "the python version on the target server is not 3.8.0"
      echo "the system may act in unintended ways"
      echo "exiting now"
      exit 1
    fi
    . "${BASE_DIR}/envCSSS/bin/activate"
  else
    python3 -m virtualenv envCSSS
    . "${BASE_DIR}/envCSSS/bin/activate"
  fi

  python3 -m pip install -r "${BASE_DIR}/requirements.txt"
}

function create_directory_for_website_logs {
  mkdir -p "${BASE_DIR}/website_logs/python_logs"
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
  if [ "${BRANCH_NAME}" == "master" ]; then
    export DB_CONTAINER_NAME="csss_site_db"
  else
    export DB_CONTAINER_NAME="csss_site_db_dev"
  fi
  docker run --name "${DB_CONTAINER_NAME}" -p "${DB_PORT}":5432 -it -d -e POSTGRES_PASSWORD="${DB_PASSWORD}" postgres:alpine || true
  wait_for_postgres_db
  if [ "${BRANCH_NAME}" != "master" ]; then
    docker exec "${DB_CONTAINER_NAME}" psql -U postgres -d postgres -c "DROP DATABASE \"${DB_NAME}\";" || true
  fi
  docker exec "${DB_CONTAINER_NAME}" psql -U postgres -d postgres -c "CREATE DATABASE \"${DB_NAME}\" OWNER postgres;" || true
}

function applying_latest_db_migrations {
  chmod +x set_env.sh
  . ./set_env.sh site_envs_django_admin

  setup_website_db

  cd "${BASE_DIR}/csss-site"
  python3 manage.py migrate
   if [ "${BRANCH_NAME}" != "master" ]; then
     python3 manage.py loaddata about
     python3 manage.py loaddata announcements/fixtures/django_mailbox.json
     python3 manage.py loaddata announcements/fixtures/announcements.json
     python3 manage.py loaddata elections
     python3 manage.py loaddata resource_management
     python3 manage.py makemigrations
     python3 manage.py migrate
  fi
}

function create_super_user {
    if [ "${BRANCH_NAME}" != "master" ]; then
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('username', 'admin@example.com', 'password')" | python3 manage.py shell || true
    fi
}

function update_static_files_location {
  # copying static files under their root directory
  python3 manage.py collectstatic --noinput

  # removing the static files that are under the source directory
  find "${BASE_DIR}/csss-site" -mindepth 1 -name 'static' -exec rm -rv {} +
}

function update_media_files {
  if [ "${BRANCH_NAME}" != "master" ]; then
    mkdir -p "${BASE_DIR}/static_root/documents_static"
    ln -s /mnt/dev_csss_website_media/event-photos "${BASE_DIR}/static_root/documents_static/" || true
    mkdir -p "${BASE_DIR}/static_root/about_static"
    ln -s /mnt/dev_csss_website_media/exec-photos "${BASE_DIR}/static_root/about_static/" || true
  fi
}

function set_gunicorn_files {
  if [ "${BRANCH_NAME}" != "master" ]; then
    echo "[Unit]
Description=gunicorn socket

[Socket]
ListenStream=${BASE_DIR}/gunicorn.sock

[Install]
WantedBy=sockets.target " | sudo tee /etc/systemd/system/gunicorn_${BRANCH_NAME}.socket

    echo "[Unit]
Description=gunicorn daemon
Requires=gunicorn_${BRANCH_NAME}.socket
After=network.target

[Service]
EnvironmentFile=${BASE_DIR}/site_envs_gunicorn
User=csss
Group=www-data
WorkingDirectory=${BASE_DIR}/csss-site
ExecStart=${BASE_DIR}/envCSSS/bin/gunicorn \\
  --access-logfile ${BASE_DIR}/website_logs/gunicorn_logs/access.log \\
  --error-logfile ${BASE_DIR}/website_logs/gunicorn_logs/error.log \\
  --disable-redirect-access-to-syslog \\
  --capture-output \\
	--timeout 120 \\
	--workers 3 \\
	--bind unix:${BASE_DIR}/gunicorn.sock \\
	csss.wsgi:application

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/gunicorn_${BRANCH_NAME}.service
  fi
  sudo systemctl daemon-reload
  }

function updating_gunincorn {
  if [ "${BRANCH_NAME}" != "master" ]; then
    gunicorn_socket="gunicorn_${BRANCH_NAME}.socket"
    gunicorn="gunicorn_${BRANCH_NAME}.service"
    socket_file_location="${BASE_DIR}/gunicorn.sock"
  else
    gunicorn_socket="gunicorn.socket"
    gunicorn="gunicorn.service"
  fi
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
  if [ "${BRANCH_NAME}" != "master" ]; then
    cd ~/
    echo -e "

    	location /${BRANCH_NAME}/STATIC_URL/ {
		proxy_read_timeout 3600;
		autoindex on;
		alias ${BASE_DIR}/static_root/;
	}
	location /${BRANCH_NAME}/MEDIA_URL/ {
		proxy_read_timeout 3600;
		autoindex on;
		alias ${BASE_DIR}/media_root/;
	}
	location /${BRANCH_NAME}/ {
		proxy_read_timeout 3600;
		include proxy_params;
		proxy_pass http://unix:${BASE_DIR}/gunicorn.sock;

	}" > "branch_${BRANCH_NAME}"
    cat /home/csss/nginx_site_config branch_* | sudo tee /etc/nginx/sites-available/PR_sites
    echo "}" | sudo tee -a /etc/nginx/sites-available/PR_sites
    sudo ln -s /etc/nginx/sites-available/PR_sites /etc/nginx/sites-enabled/ || true
    sudo nginx -t
  fi
  sudo systemctl restart nginx

}

function clean_up_after_deployment {
  if [ "${BRANCH_NAME}" != "master" ]; then
    rm "${BASE_DIR}/deploy_changes.sh"
  else
    rm "/home/csss/deploy_changes.sh"
  fi
}


go_to_root_directory
install_latest_python_requirements
create_directory_for_website_logs
applying_latest_db_migrations
create_super_user
update_static_files_location
update_media_files
set_gunicorn_files
updating_gunincorn
update_nginx_configuration
clean_up_after_deployment
