#!/bin/bash

set -e -o xtrace

function remove_existing_files {
  # remove all old and replace with newer code. will make sure that the migrations are not deleted as they need to be
  # persistent through the changes
#  ssh csss@"${HOST_ADDRESS}" \
#      "rm -fr ${BASE_DIR}/csss-site" \
#      || true
#  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/deploy_changes.sh" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/site_envs" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/site_envs_django_admin" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/site_envs_gunicorn" || true
#  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/set_env.sh" || true
#  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/requirements.txt" || true

}

function transfer_source_code_and_reqs {
  # create the folder that the source code for the website will go under
  # and copy the source code to that folder
  ssh csss@"${HOST_ADDRESS}" "mkdir -p ${BASE_DIR}/csss-site"
  scp -r "csss-site/src"/* csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss-site/"

  # transfer requirements file for the website
  scp "requirements.txt" csss@"${HOST_ADDRESS}":"${BASE_DIR}/requirements.txt"
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
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs"'" > site_envs_django_admin
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/gunicorn_logs"'" > site_envs_gunicorn

  if [[ "${BRANCH_NAME}" != "master" ]]; then
    echo 'DB_NAME='"'"${BRANCH_NAME}"'" >> site_envs
    echo 'CHANGE_ID='"'"${CHANGE_ID}"'" >> site_envs

  else
    echo 'DB_NAME='"'postgres'" >> site_envs
  fi
  cat site_envs >> site_envs_django_admin
  cat site_envs >>  site_envs_gunicorn
  scp site_envs_django_admin csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs_django_admin"
  scp site_envs_gunicorn csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs_gunicorn"
#  scp "CI/validate_and_deploy/2_deploy/set_env.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/set_env.sh"
}

function transfer_file_to_deploy_all_above_changes {
  scp "CI/validate_and_deploy/2_deploy/2_deploy_changes.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/deploy_changes.sh"
}

remove_existing_files
# transfer_source_code_and_reqs
transfer_env_variables_to_server
transfer_file_to_deploy_all_above_changes
