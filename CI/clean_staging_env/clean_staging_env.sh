#!/bin/bash

set -e -o xtrace


function help(){
	echo "Mandatory arguments"
	echo -e "\t-staging_name, -pr_number"
	exit 0
}

while [ "$#" -gt 0 ]
do
	if [ "${1}" = "-staging_name" ]; then
		export STAGING_NAME="${2}"
		shift
		shift
	elif [ "${1}" = "-pr_number" ]; then
		export PR_NUMBER="${2}"
		shift
		shift
	elif [ "${1}" = "-h" ]; then
		help
	else
		echo -e "\nUnrecognized flag \"${1}\"\n"
		help
	fi
done

if [ -z $STAGING_NAME ] && [ -z $PR_NUMBER ]; then
  echo "Please specify one of the following arguments: -staging_name, -pr_number"
  exit 1
fi

if [ ! -z $STAGING_NAME ] && [ ! -z $PR_NUMBER ]; then
  echo "Please specify only one of the following arguments: -staging_name, -pr_number"
  exit 1
fi

if [ -z $STAGING_NAME ]; then
  STAGING_NAME="PR-${PR_NUMBER}"
fi

function remove_website_code(){
	rm -fr /home/csss/${STAGING_NAME} || true
}

function remove_nginx_config(){
	rm -fr /home/csss/branch_${STAGING_NAME} || true
	cat /home/csss/1_nginx_config_file branch_* /home/csss/2_nginx_conf_file \
	 | sudo tee /etc/nginx/sites-available/PR_sites
	rm /home/csss/1_nginx_config_file /home/csss/2_nginx_conf_file
	sudo nginx -t
	sudo systemctl restart nginx
}

function remove_gunicorn_systemd_files(){
	gunicorn_socket="gunicorn_${STAGING_NAME}.socket"
	gunicorn="gunicorn_${STAGING_NAME}.service"

	sudo systemctl stop "${gunicorn_socket}" || true
	sudo systemctl disable "${gunicorn_socket}" || true

	sudo systemctl stop "${gunicorn}" || true
	sudo systemctl disable "${gunicorn}" || true

	sudo rm /etc/systemd/system/"${gunicorn_socket}" || true
	sudo rm /etc/systemd/system/"${gunicorn}" || true

	sudo systemctl daemon-reload
}

function remove_database(){
	  docker exec csss_site_db_dev psql -U postgres -d postgres -c "DROP DATABASE \"${STAGING_NAME}\";" || true
}
remove_website_code

remove_nginx_config

remove_gunicorn_systemd_files

remove_database
