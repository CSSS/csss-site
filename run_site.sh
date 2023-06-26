#!/bin/bash

set -e

echo -e "\n[y/N] indicates a yes/no question. the default is the letter in CAPS. If answer is not understood, will revert to default\n"

echo "Do you need to run through the setup? [y/N]"
read run_through_setup
if [ "${run_through_setup}" == "y" ];
then
  use_defaults="false";
  if [ "${1}" == "--default" ];
  then
    use_defaults="true";
    dockerized_database="n";
    work_on_front_page="n";
    work_on_officer_list_page="n";
    launch_website="y";
  fi

  if [ "${use_defaults}" != "true" ];
  then
    echo "Do you want to use docker for the database? [y/N]"
    read dockerized_database
  fi
  if [[ "$OSTYPE" == "linux-gnu"* ]];
  then
    supported_os="true"
  else
    supported_os="false"
  fi
  if [[ "${dockerized_database}" == "y" && "${supported_os}" == "false" ]];
  then
    echo "sorry, script is not currently setup to use docker for database on non-linux system :-("
    echo "Please feel free to add that feature in"
    exit 1
  fi

  if [ "${use_defaults}" != "true" ];
  then
    echo "Do you need to work on the front page? [the announcements page]  [y/N]"
    read work_on_front_page
  fi

  if [ "${work_on_front_page}" == "y" ];
  then
    echo "Do you need the actual attachments when working on the front page? [if in doubt, then the answer is no] [y/N]"
    read work_on_front_page_with_live_data
  else
    work_on_front_page_with_live_data='n'
  fi

  if [ "${use_defaults}" != "true" ];
  then
    echo "Do you need to work on the page that list the officers? [y/N]"
    read work_on_officer_list_page
  fi

  if [ "${work_on_officer_list_page}" == "y" ];
  then
    echo "Do you need the actual officer pics when working on page that has the list of officers? [y/N]"
    read work_on_officer_list_page_with_live_data
  else
    work_on_officer_list_page_with_live_data='n'
  fi

  if [ "${use_defaults}" != "true" ];
  then
    echo "Do you you want this script to launch the website? [Yn] [the alternative is to use PyCharm]"
    read launch_website
  fi

  base_dir=$(pwd)
  log_Location=${base_dir}"/website_logs/python_logs"

  echo 'BASE_DIR='"'"${base_dir}"'" > CI/validate_and_deploy/2_deploy/csss_site.env
  echo 'ENVIRONMENT='"'"'LOCALHOST'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
  echo 'LOG_LOCATION='"'"${log_Location}"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
  if [ "${dockerized_database}" == "y" ];
  then
    echo 'DB_TYPE='"'"'postgres'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
    echo 'DB_PASSWORD='"'"'test_password'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
    echo 'DB_NAME='"'"'csss_website_db'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
    echo 'DB_PORT='"'"'5432'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
    echo 'DB_CONTAINER_NAME='"'"'csss_website_dev_db'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
  else
    echo 'DB_TYPE='"'"'sqlite3'"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
  fi

  python3 -m pip install -r requirements.txt
  python3 -m pip install --ignore-installed six

  cd csss-site/src

  . ../../CI/validate_and_deploy/2_deploy/set_env.sh csss_site.env

  mkdir -p "${log_Location}"

  if [[ "${dockerized_database}" == "y" ]];
  then
      sudo apt-get install postgresql-contrib
      ../../CI/fixtures_and_media_download/create_dockerized_database_with_migration.sh
  else
      ../../CI/fixtures_and_media_download/create_sqlite_database_with_migration.sh
  fi

  if [ "${work_on_front_page_with_live_data}" == "y" ];
  then
    python3 manage.py create_attachments  --download
  elif [ "${work_on_front_page}" == "y" ];
  then
    python3 manage.py create_attachments
  fi

  if [ "${work_on_officer_list_page_with_live_data}" == "y" ];
  then
    python3 manage.py update_officer_images --download
  elif [ "${work_on_officer_list_page}" == "y" ];
  then
    python3 manage.py update_officer_images
  fi

  echo "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'admin@example.com', 'password')" | python3 manage.py shell || true
  if [ "${launch_website}" == "n" ];
  then
    echo "Seems you are going to use something else to launch the site. If you are going to use PyCharm, I HIGHLY recommend using https://github.com/ashald/EnvFile"
  fi
else
  launch_website="y"
fi

if [ "${launch_website}" != "n" ];
then
  echo "Launching the website...if you need to log into 127.0.0.1:8000/admin, the credentials are root/password"
  sleep 3
  python3 manage.py runserver 127.0.0.1:8000
fi