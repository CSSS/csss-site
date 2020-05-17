#!/bin/bash

set -e -o xtrace


export PR_NAME="PR-${1}"

function remove_wbsite_code(){
	rm -fr /home/csss/${PR_NAME} || true
}

function remove_nginx_config(){
	rm -fr /home/csss/branch_${PR_NAME} || true
	cat /home/csss/nginx_site_config branch_* | sudo tee /etc/nginx/sites-available/PR_sites
	echo "}" | sudo tee -a /etc/nginx/sites-available/PR_sites
	sudo nginx -t
	sudo systemctl restart nginx
}

function remove_gunicorn_sytemd_files{
	gunicorn_socket="gunicorn_${PR_NAME}.socket"
	gunicorn="gunicorn_${PR_NAME}.service"
	socket_file_location="/home/csss/${PR_NAME}/gunicorn.sock"

	sudo systemctl stop "${gunicorn_socket}"
	sudo systemctl disable "${gunicorn_socket}"

	sudo systemctl stop "${gunicorn}"
	sudo systemctl disable "${gunicorn}"

	sudo rm /etc/systemd/system/gunicorn_${PR_NAME}.socket
	sudo rm /etc/systemd/system/gunicorn_${PR_NAME}.service
}

remove_wbsite_code

remove_nginx_config

remove_gunicorn_sytemd_files
