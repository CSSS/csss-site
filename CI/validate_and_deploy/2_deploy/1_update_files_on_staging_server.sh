#!/bin/bash

set -e -o xtrace

function create_staging_branch_home_dir {
  ssh csss@"${HOST_ADDRESS}" "rm -fr ${BASE_DIR}" || true
  ssh csss@"${HOST_ADDRESS}" "mkdir -p ${BASE_DIR}" || true
}

function remove_existing_files {
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/csss_site_envs/csss_site_django_admin.env" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/csss_site_envs/csss_site_gunicorn.env" || true

}

function transfer_env_variables_to_server {
  # create the file that contains all the environment variables that
  # site needs to run
  echo 'BASE_DIR='"'"${BASE_DIR}"'" > csss_site.env
  echo 'WEBSITE_SECRET_KEY='"'"${WEBSITE_SECRET_KEY}"'" >> csss_site.env
  echo 'DEBUG='"'"${DEBUG}"'" >> csss_site.env
  echo 'HOST_ADDRESS='"'"${HOST_ADDRESS}"'" >> csss_site.env
  echo 'DB_PASSWORD='"'"${DB_PASSWORD}"'" >> csss_site.env
  echo 'STRIPE_PUBLISHABLE_KEY='"'"${STRIPE_PUBLISHABLE_KEY}"'" >> csss_site.env
  echo 'STRIPE_SECRET_KEY='"'"${STRIPE_SECRET_KEY}"'" >> csss_site.env
  echo 'DB_PORT='"'"'5432'"'" >> csss_site.env
  echo 'DB_TYPE='"'"'postgres'"'" >> csss_site.env
  echo 'BRANCH_NAME='"'"${BRANCH_NAME}"'" >> csss_site.env
  echo 'ENVIRONMENT='"'"${ENVIRONMENT}"'" >> csss_site.env

  echo 'GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS='"'"${GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS}"'" >> csss_site.env
  echo 'GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY='"'"${GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY}"'" >> csss_site.env
  echo 'GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY='"'"${GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY}"'" >> csss_site.env
  echo 'GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY='"'"${GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY}"'" >> csss_site.env
  echo 'GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY='"'"${GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY}"'" >> csss_site.env
  echo 'GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC='"'"${GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC}"'" >> csss_site.env
  echo 'GDRIVE_ROOT_FOLDER_ID='"'"${GDRIVE_ROOT_FOLDER_ID}"'" >> csss_site.env

  echo 'GDRIVE_TOKEN_LOCATION='"'"${GDRIVE_TOKEN_LOCATION}"'" >> csss_site.env
  echo 'GITHUB_ACCESS_TOKEN='"'"${GITHUB_ACCESS_TOKEN}"'" >> csss_site.env
  echo 'SFU_CSSS_GMAIL_USERNAME='"'"${SFU_CSSS_GMAIL_USERNAME}"'" >> csss_site.env
  echo 'SFU_CSSS_GMAIL_PASSWORD='"'"${SFU_CSSS_GMAIL_PASSWORD}"'" >> csss_site.env
  echo 'DISCORD_BOT_TOKEN='"'"${DISCORD_BOT_TOKEN}"'" >> csss_site.env
  echo 'GUILD_ID='"'"${GUILD_ID}"'" >> csss_site.env
  echo 'SFU_ENDPOINT_TOKEN='"'"${SFU_ENDPOINT_TOKEN}"'" >> csss_site.env
  echo 'DB_CONTAINER_NAME='"'"'csss_site_db_dev'"'" >> csss_site.env
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/django_admin"'" > csss_site_django_admin.env
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/gunicorn_logs"'" > csss_site_gunicorn.env
  echo 'DB_NAME='"'"${BRANCH_NAME}"'" >> csss_site.env
  echo 'CHANGE_ID='"'"${CHANGE_ID}"'" >> csss_site.env

  cat csss_site.env >> csss_site_django_admin.env
  cat csss_site.env >>  csss_site_gunicorn.env
  ssh csss@"${HOST_ADDRESS}" "mkdir -p ${BASE_DIR}/csss_site_envs" || true
  scp csss_site_django_admin.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_django_admin.env"
  scp csss_site_gunicorn.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_gunicorn.env"
}

function transfer_file_to_deploy_all_above_changes {
  scp "CI/validate_and_deploy/2_deploy/2_deploy_staging_changes.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/deploy_changes.sh"
}

create_staging_branch_home_dir
remove_existing_files
transfer_env_variables_to_server
transfer_file_to_deploy_all_above_changes
