#!/bin/bash

set -e -o xtrace

if [ -z "${TARGET_SERVER}" -o -z "${BASE_DIR}" -o -z "${WEBSITE_SECRET_KEY}" \
  -o -z "${DEBUG}" -o -z "${HOST_ADDRESS}" -o -z "${DB_PASSWORD}" \
  -o -z "${STRIPE_PUBLISHABLE_KEY}" -o -z "${STRIPE_SECRET_KEY}"]; then
    echo "not all necessary env variables are detected, please export following variables: "
    echo "TARGET_SERVER, BASE_DIR, WEBSITE_SECRET_KEY, DEBUG, HOST_ADDRESS, DB_PASSWORD \
    STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY"
    exit 1
fi



function determine_base_file_path {
  if [ "${BRANCH_NAME}" != "master" ]; then
    export FILE_PATH="/home/csss/${PR_NUMBER}"
  else
    export FILE_PATH="/home/csss"
  fi
}

function remove_existing_files {
  # remove all old and replace with newer code. will make sure that the migrations are not deleted as they need to be
  # persistent through the changes
  if [ "${BRANCH_NAME}" != "master" ]; then
    ssh csss@"${TARGET_SERVER}" "rm ${FILE_PATH}/update_nginx_conf.sh" || true
  fi
  ssh csss@"${TARGET_SERVER}" \
      "find ${FILE_PATH}/csss-site/csss-site/src -mindepth 1 ! -regex '.*migrations.*' -delete" \
      || true
  ssh csss@"${TARGET_SERVER}" "rm ${FILE_PATH}/csss-site/requirements.txt" || true
  ssh csss@"${TARGET_SERVER}" "rm ${FILE_PATH}/deploy_changes.sh" || true
  ssh csss@"${TARGET_SERVER}" "rm ${FILE_PATH}/site_envs" || true
  ssh csss@"${TARGET_SERVER}" "rm ${FILE_PATH}/set_env.sh" || true
  ssh csss@"${TARGET_SERVER}" "rm ${FILE_PATH}/migrate_apps.sh" || true

}

function transfer_source_code_and_reqs {
  # create the folder that the source code for the website will go under
  # and copy the source code to that folder
  ssh csss@"${TARGET_SERVER}" "mkdir -p ${FILE_PATH}/csss-site/csss-site/src"
  scp -r "csss-site/src"/* csss@"${TARGET_SERVER}":"${FILE_PATH}/csss-site/csss-site/src/"

  # transfer requirements file for the website
  scp "requirements.txt" csss@"${TARGET_SERVER}":"${FILE_PATH}/csss-site/requirements.txt"
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
  echo 'CHANGE_ID='"'"${CHANGE_ID}"'" >> site_envs
  scp site_envs csss@"${TARGET_SERVER}":"${FILE_PATH}/site_envs"
  scp "CI/set_env.sh" csss@"${TARGET_SERVER}":"${FILE_PATH}/set_env.sh"
}

function transfer_file_for_automating_app_migration {
  scp CI/migrate_apps.sh csss@"${TARGET_SERVER}":"${FILE_PATH}/migrate_apps.sh"
}

function transfer_nginx_configuration_script {
  if [ "${BRANCH_NAME}" != "master" ]; then
    scp CI/update_nginx_conf.sh csss@"${TARGET_SERVER}":"${FILE_PATH}/update_nginx_conf.sh"
  fi
}

function transfer_file_to_deploy_all_above_changes {
  scp "CI/deploy_changes.sh" csss@"${TARGET_SERVER}":"${FILE_PATH}/deploy_changes.sh"
}

determine_base_file_path
remove_existing_files
transfer_source_code_and_reqs
transfer_env_variables_to_server
transfer_file_for_automating_app_migration
transfer_nginx_configuration_script
transfer_file_to_deploy_all_above_changes
