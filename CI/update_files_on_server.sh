#!/bin/bash

set -e -o xtrace

function remove_existing_files {
  # remove all old and replace with newer code. will make sure that the migrations are not deleted as they need to be
  # persistent through the changes
  ssh csss@"${TARGET_SERVER}" \
      "find /home/csss/csss-site/csss-site/src -mindepth 1 ! -regex '.*migrations.*' -delete" \
      || true
  ssh csss@"${TARGET_SERVER}" "rm /home/csss/csss-site/requirements.txt" || true
  ssh csss@"${TARGET_SERVER}" "rm /home/csss/deploy_changes.sh" || true
  ssh csss@"${TARGET_SERVER}" "rm /home/csss/site_envs" || true
  ssh csss@"${TARGET_SERVER}" "rm /home/csss/set_env.sh" || true
  ssh csss@"${TARGET_SERVER}" "rm /home/csss/migrate_apps.sh" || true
}

function transfer_source_code_and_reqs {
  # create the folder that the source code for the website will go under
  # and copy the source code to that folder
  ssh csss@"${TARGET_SERVER}" "mkdir -p /home/csss/csss-site/csss-site/src"
  scp -r "csss-site/src"/* csss@"${TARGET_SERVER}":/home/csss/csss-site/csss-site/src/

  # transfer requirements file for the website
  scp "requirements.txt" csss@"${TARGET_SERVER}":/home/csss/csss-site/requirements.txt
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
  scp site_envs csss@"${TARGET_SERVER}":/home/csss/site_envs
  scp "CI/set_env.sh" csss@"${TARGET_SERVER}":/home/csss/set_env.sh
}

function transfer_file_for_automating_app_migration {
  scp CI/migrate_apps.sh csss@"${TARGET_SERVER}":/home/csss/migrate_apps.sh
}

function transfer_file_to_deploy_all_above_changes {
  scp "CI/deploy_changes.sh" csss@"${TARGET_SERVER}":/home/csss/deploy_changes.sh
}

echo "${TARGET_SERVER}"
echo "${DEBUG}"
remove_existing_files
transfer_source_code_and_reqs
transfer_env_variables_to_server
transfer_file_for_automating_app_migration
transfer_file_to_deploy_all_above_changes
