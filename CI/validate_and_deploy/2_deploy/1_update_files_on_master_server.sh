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
  ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/site_envs/*" || true
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
  echo 'SFU_CSSS_GMAIL_USERNAME='"'"${SFU_CSSS_GMAIL_USERNAME}"'" >> site_envs
  echo 'SFU_CSSS_GMAIL_PASSWORD='"'"${SFU_CSSS_GMAIL_PASSWORD}"'" >> site_envs
  echo 'DISCORD_BOT_TOKEN='"'"${DISCORD_BOT_TOKEN}"'" >> site_envs
  echo 'GUILD_ID='"'"${GUILD_ID}"'" >> site_envs
  echo 'SFU_ENDPOINT_TOKEN='"'"${SFU_ENDPOINT_TOKEN}"'" >> site_envs
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/gunicorn_logs"'" > site_envs_gunicorn  
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/backup_script"'" > site_envs_backup_script
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/create_fixtures"'" > site_envs_create_fixtures
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/django_admin"'" > site_envs_django_admin
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/jenkins"'" > site_envs_jenkins
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/process_announcements"'" > site_envs_process_announcements
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/update_officer_pics"'" > site_envs_update_officer_pics
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/validate_resource_permissions"'" > site_envs_validate_resource_permissions    
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/nag_officers_to_enter_info"'" > site_envs_nag_officers_to_enter_info
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/update_discord_details"'" > site_envs_update_discord_details
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/validate_discord_roles_members"'" > site_envs_validate_discord_roles_members
  echo 'LOG_LOCATION='"'"${BASE_DIR}/website_logs/python_logs/csss_website_cron_job"'" > site_envs_csss_website_cron_job
  echo 'DB_NAME='"'postgres'" >> site_envs

  cat site_envs >> site_envs_gunicorn
  cat site_envs >> site_envs_backup_script
  cat site_envs >> site_envs_create_fixtures
  cat site_envs >> site_envs_django_admin
  cat site_envs >> site_envs_jenkins
  cat site_envs >> site_envs_process_announcements
  cat site_envs >> site_envs_update_officer_pics
  cat site_envs >> site_envs_validate_resource_permissions
  cat site_envs >> site_envs_nag_officers_to_enter_info
  cat site_envs >> site_envs_update_discord_details
  cat site_envs >> site_envs_validate_discord_roles_members
  cat site_envs >> site_envs_csss_website_cron_job

  scp site_envs_gunicorn csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_gunicorn"
  scp site_envs_backup_script csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_backup_script"
  scp site_envs_create_fixtures csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_create_fixtures"
  scp site_envs_django_admin csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_django_admin"
  scp site_envs_jenkins csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_jenkins"
  scp site_envs_process_announcements csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_process_announcements"
  scp site_envs_update_officer_pics csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_update_officer_pics"
  scp site_envs_validate_resource_permissions csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_validate_resource_permissions"
  scp site_envs_nag_officers_to_enter_info csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_nag_officers_to_enter_info"
  scp site_envs_update_discord_details csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_update_discord_details"
  scp site_envs_validate_discord_roles_members csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_validate_discord_roles_members"
  scp site_envs_csss_website_cron_job csss@"${HOST_ADDRESS}":"${BASE_DIR}/site_envs/site_envs_csss_website_cron_job"
  scp "CI/validate_and_deploy/2_deploy/set_env.sh" csss@"${HOST_ADDRESS}":"${BASE_DIR}/set_env.sh"
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