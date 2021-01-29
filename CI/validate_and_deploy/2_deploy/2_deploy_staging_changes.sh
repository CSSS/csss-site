#!/bin/bash

set -e -o xtrace



function go_to_root_directory {
  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
  cd "${BASE_DIR}"
}

function create_directory_for_website_logs {
  mkdir -p "${BASE_DIR}/website_logs/python_logs"
  mkdir -p "${BASE_DIR}/website_logs/gunicorn_logs"
}

function clone_website {
  rm -fr csss-site csss-site-repo || true
  git clone https://github.com/CSSS/csss-site.git
  cd csss-site
  git checkout migration_CI
  cd -
}

function setup_master_virtual_env(){
  python3 -m pip install virtualenv
  rm -fr "${BASE_DIR}/envCSSS_master"
  python3 -m virtualenv envCSSS_master
  . "${BASE_DIR}/envCSSS_master/bin/activate"
  python3 -m pip install -r "${BASE_DIR}/csss-site/requirements.txt" --no-cache-dir


  chmod +x "${BASE_DIR}/csss-site/CI/validate_and_deploy/2_deploy/set_env.sh"
  cp "${BASE_DIR}/csss-site/CI/validate_and_deploy/2_deploy/set_env.sh" "${BASE_DIR}/set_env.sh"
  . "${BASE_DIR}/set_env.sh" site_envs_django_admin
}


function setup_db_and_apply_master_migrations {
  cd "${BASE_DIR}/csss-site/csss-site/src"
  git checkout migration_CI
  ../../migrations/1_update_fixtures.sh
  docker stop "${DB_CONTAINER_NAME}" || true
  docker rm "${DB_CONTAINER_NAME}" || true
  ../../migrations/2_apply_dockerized_database_migration.sh
}

function switch_to_pr_branch(){
  deactivate
  cd "${BASE_DIR}/csss-site"
  git fetch origin "pull/${CHANGE_ID}/head:pr-${CHANGE_ID}"
  git reset --hard
  git checkout "pr-${CHANGE_ID}"
  rm -fr "${BASE_DIR}/envCSSS_master" "${BASE_DIR}/envCSSS"
  cd "${BASE_DIR}"
  python3 -m virtualenv envCSSS
  . "${BASE_DIR}/envCSSS/bin/activate"
  python3 -m pip install -r "${BASE_DIR}/csss-site/requirements.txt" --no-cache-dir
}

function organize_file_structure {
  cd "${BASE_DIR}"
  mv "${BASE_DIR}/csss-site" "${BASE_DIR}/csss-site-repo"
  mv "${BASE_DIR}/csss-site-repo/csss-site/src" csss-site
  mv "${BASE_DIR}/csss-site-repo/requirements.txt" requirements.txt
  rm -fr "${BASE_DIR}/csss-site-repo"
  cd "${BASE_DIR}/csss-site"
}

function apply_pr_migrations(){
  cd "${BASE_DIR}/csss-site"
  python3 manage.py migrate
}

function create_super_user {
  cd "${BASE_DIR}/csss-site"
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('username', 'admin@example.com', 'password')" | python3 manage.py shell || true
}

function update_static_files_location {
  # copying static files under their root directory
  python3 manage.py collectstatic --noinput

  # removing the static files that are under the source directory
  find "${BASE_DIR}/csss-site" -mindepth 1 -name 'static' -exec rm -rv {} +
}

function update_media_files {
  mkdir -p "${BASE_DIR}/static_root/documents_static"
  ln -ns /mnt/dev_csss_website_media/event-photos "${BASE_DIR}/static_root/documents_static/" || true
  mkdir -p "${BASE_DIR}/static_root/about_static"
  ln -ns /mnt/dev_csss_website_media/exec-photos "${BASE_DIR}/static_root/about_static/" || true
}

function set_gunicorn_files {
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
  sudo systemctl daemon-reload
  }

function updating_gunincorn {
  gunicorn_socket="gunicorn_${BRANCH_NAME}.socket"
  gunicorn="gunicorn_${BRANCH_NAME}.service"
  socket_file_location="${BASE_DIR}/gunicorn.sock"
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
  sudo systemctl restart nginx

}

function clean_up_after_deployment {
  rm "${BASE_DIR}/deploy_changes.sh"
}


go_to_root_directory
create_directory_for_website_logs
clone_website
setup_master_virtual_env
setup_db_and_apply_master_migrations
switch_to_pr_branch
organize_file_structure
apply_pr_migrations
create_super_user
update_static_files_location
update_media_files
set_gunicorn_files
updating_gunincorn
update_nginx_configuration
clean_up_after_deployment
