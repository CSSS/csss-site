#!/bin/bash

set -e -o xtrace

# https://stackoverflow.com/a/5750463/7734535

if [ -z "${VIRTUAL_ENV}" ]; then
	echo "please active a python virtual environment before using this script"
	exit 1
fi

# need to delete and re-create so that the if statement that tries to detected if the
# help menu was invoked can work correctly
cat ./CI/validate_and_deploy/2_deploy/run_csss_site.env | grep -v HELP_SELECTED > ./CI/validate_and_deploy/2_deploy/run_csss_site.env.2 || true
mv ./CI/validate_and_deploy/2_deploy/run_csss_site.env.2 ./CI/validate_and_deploy/2_deploy/run_csss_site.env

./.run_site.py $@

while [ "$#" -gt 0 ]
do
    shift
done

. ./CI/validate_and_deploy/2_deploy/set_env.sh
. ./CI/validate_and_deploy/2_deploy/set_env_master.sh run_csss_site.env

if [ -z "${HELP_SELECTED}" ]; then
	exit 0
fi

if [ -z "${BASE_DIR}" ]; then
	BASE_DIR=$(pwd)
	echo -e '\n\nBASE_DIR='"'"${BASE_DIR}"'" >> CI/validate_and_deploy/2_deploy/csss_site.env
	echo 'LOG_LOCATION='"'"${BASE_DIR}"/website_logs/python_logs""'" >> CI/validate_and_deploy/2_deploy/csss_site.env
	. ./CI/validate_and_deploy/2_deploy/set_env.sh
fi



pushd csss-site/src

if [[ "${INSTALL_REQUIREMENTS}" == "True" ]]; then
	python3 -m pip install -r ../../requirements.txt
	python3 -m pip install --ignore-installed six
fi

if [[ "${SETUP_DATABASE}" == "True" ]]; then
	if [[ "${DB_TYPE}" == "sqlite3" ]]; then
		git checkout master
		rm db.sqlite3 || true
		python3 manage.py migrate
		rm csss_cron_info.json elections.json errors.json about.json resource_management.json || true
		wget https://dev.sfucsss.org/website/fixtures/csss_cron_info.json
		wget https://dev.sfucsss.org/website/fixtures/elections.json
		wget https://dev.sfucsss.org/website/fixtures/errors.json
		wget https://dev.sfucsss.org/website/fixtures/about.json
		wget https://dev.sfucsss.org/website/fixtures/resource_management.json
		python3 manage.py loaddata csss_cron_info.json
		python3 manage.py loaddata elections.json
		python3 manage.py loaddata errors.json
		python3 manage.py loaddata about.json
		python3 manage.py loaddata resource_management.json
		rm csss_cron_info.json elections.json errors.json about.json resource_management.json
		git checkout -
	else
		dpkg -s postgresql-contrib &> /dev/null
		if [[ $? -eq 1 ]]; then
			sudo apt-get install postgresql-contrib
		fi
		../../CI/fixtures_and_media_download/create_dockerized_database_with_migration.sh
	fi
fi

if [[ "${DOWNLOAD_ANNOUNCEMENTS}" == "True" ]] || [[ "${DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS}" == "True" ]]; then
	setup_front_page="python3 manage.py create_attachments"
	if [[ "${DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS}" == "True" ]]; then
		setup_front_page+=" --download"
	fi
	rm announcements.json django_mailbox.json || true
	wget https://dev.sfucsss.org/website/fixtures/announcements.json
	wget https://dev.sfucsss.org/website/fixtures/django_mailbox.json
	python3 manage.py loaddata django_mailbox.json
	python3 manage.py loaddata announcements.json
	rm announcements.json django_mailbox.json
	${setup_front_page}
fi

if [[ "${SETUP_OFFICER_LIST}" == "True" ]] || [[ "${SETUP_OFFICER_LIST_IMAGES}" == "True" ]]; then
	setup_officer_list_page="python3 manage.py update_officer_images"
	if [[ "${SETUP_OFFICER_LIST_IMAGES}" == "True" ]]; then
		setup_officer_list_page+=" --download"
	fi
	${setup_officer_list_page}
fi

echo "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'admin@example.com', 'password')" | python3 manage.py shell || true

if [[ "${LAUNCH_WEBSITE}" == "True" ]]; then
  echo "Launching the website...if you need to log into 127.0.0.1:8000/admin, the credentials are root/password"
  sleep 3
  python3 manage.py runserver 127.0.0.1:8000
else
  echo "Seems you are going to use something else to launch the site. If you are going to use PyCharm, I HIGHLY recommend using https://github.com/ashald/EnvFile"
fi