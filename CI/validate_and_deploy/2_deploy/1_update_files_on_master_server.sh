#!/bin/bash

set -e -o xtrace

function switch_nginx_to_construction_page {
  ssh csss@"${HOST_ADDRESS}" "sudo rm /etc/nginx/sites-enabled/website; sudo ln -s /etc/nginx/sites-available/construction /etc/nginx/sites-enabled/website; sudo systemctl restart nginx.service"
  scp "CI/validate_and_deploy/2_deploy/Under-Construction1.jpg" csss@"${HOST_ADDRESS}":"${BASE_DIR}/Under-Construction1.jpg"
}

function remove_existing_files {
  # remove all old and replace with newer code. will make sure that the migrations are not deleted as they need to be
  # persistent through the changes
  ssh csss@"${HOST_ADDRESS}" \
      "rm -fr ${BASE_DIR}/csss-site" \
      || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/deploy_changes.sh" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/csss_site_envs/*" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/set_env.sh" || true
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/requirements.txt" || true
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
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/gunicorn_logs"'" > csss_site_gunicorn.env
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/backup_script"'" > csss_site_backup_script.env
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/create_fixtures"'" > csss_site_create_fixtures.env
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/django_admin"'" > csss_site_django_admin.env
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/jenkins"'" > csss_site_jenkins.env
  echo 'DB_NAME='"'postgres'" >> csss_site.env

  cat csss_site.env >> csss_site_gunicorn.env
  cat csss_site.env >> csss_site_backup_script.env
  cat csss_site.env >> csss_site_create_fixtures.env
  cat csss_site.env >> csss_site_django_admin.env
  cat csss_site.env >> csss_site_jenkins.env

  scp csss_site_gunicorn.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_gunicorn.env"
  scp csss_site_backup_script.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_backup_script.env"
  scp csss_site_create_fixtures.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_create_fixtures.env"
  scp csss_site_django_admin.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_django_admin.env"
  scp csss_site_jenkins.env csss@"${HOST_ADDRESS}":"${BASE_DIR}/csss_site_envs/csss_site_jenkins.env"
  scp "CI/validate_and_deploy/2_deploy/set_env_master.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/set_env.sh"
}

function transfer_file_to_deploy_all_above_changes {
  scp "CI/validate_and_deploy/2_deploy/2_deploy_master_changes.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/deploy_changes.sh"
}

function switch_nginx_back_to_website {
  ssh csss@"${HOST_ADDRESS}" "sudo rm /etc/nginx/sites-enabled/website; sudo ln -s /etc/nginx/sites-available/website /etc/nginx/sites-enabled/website; sudo systemctl restart nginx.service"
}

switch_nginx_to_construction_page
remove_existing_files
transfer_source_code_and_reqs
transfer_env_variables_to_server
transfer_file_to_deploy_all_above_changes
switch_nginx_back_to_website