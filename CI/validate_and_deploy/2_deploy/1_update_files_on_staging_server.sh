#!/bin/bash

set -e -o xtrace

function create_staging_branch_home_dir {
  ssh csss@"${HOST_ADDRESS}" "mkdir -p ${BASE_DIR}" || true
}

function remove_existing_files {
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/site_envs/site_envs_django_admin" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/site_envs/site_envs_gunicorn" || true

}

function transfer_env_variables_to_server {
  # create the file that contains all the environment variables that
  # site needs to run
  echo 'BASE_DIR='"'"${BASE_DIR}"'" > site_envs
  echo 'WEBSITE_SECRET_KEY='"'"${WEBSITE_SECRET_KEY}"'" >> site_envs
  echo 'DEBUG='"'"${DEBUG}"'" >> site_envs
  echo 'HOST_ADDRESS='"'"${HOST_ADDRESS}"'" >> site_envs
  echo 'DB_PASSWORD='"'"${DB_PASSWORD}"'" >> site_envs
  echo 'STRIPE_PUBLISHABLE_KEY='"'"${STRIPE_PUBLISHABLE_KEY}"'" >> site_envs
  echo 'STRIPE_SECRET_KEY='"'"${STRIPE_SECRET_KEY}"'" >> site_envs
  echo 'DB_PORT='"'"'5432'"'" >> site_envs
  echo 'DB_TYPE='"'"'postgres'"'" >> site_envs
  echo 'BRANCH_NAME='"'"${BRANCH_NAME}"'" >> site_envs
  echo 'ENVIRONMENT='"'"${ENVIRONMENT}"'" >> site_envs
  echo 'GDRIVE_ROOT_FOLDER_ID='"'"${GDRIVE_ROOT_FOLDER_ID}"'" >> site_envs
  echo 'GDRIVE_TOKEN_LOCATION='"'"${GDRIVE_TOKEN_LOCATION}"'" >> site_envs
  echo 'GITHUB_ACCESS_TOKEN='"'"${GITHUB_ACCESS_TOKEN}"'" >> site_envs
  echo 'GITLAB_PRIVATE_TOKEN='"'"${GITLAB_PRIVATE_TOKEN}"'" >> site_envs
  echo 'DB_CONTAINER_NAME='"'"'csss_site_db_dev'"'" >> site_envs
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/django_admin"'" > site_envs_django_admin
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/gunicorn_logs"'" > site_envs_gunicorn
  echo 'DB_NAME='"'"${BRANCH_NAME}"'" >> site_envs
  echo 'CHANGE_ID='"'"${CHANGE_ID}"'" >> site_envs

  cat site_envs >> site_envs_django_admin
  cat site_envs >>  site_envs_gunicorn
  scp site_envs_django_admin csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_django_admin"
  scp site_envs_gunicorn csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_gunicorn"
}

function transfer_file_to_deploy_all_above_changes {
  scp "CI/validate_and_deploy/2_deploy/2_deploy_staging_changes.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/deploy_changes.sh"
}

create_staging_branch_home_dir
remove_existing_files
transfer_env_variables_to_server
transfer_file_to_deploy_all_above_changes
