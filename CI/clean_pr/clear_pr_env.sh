#!/bin/bash

set -e -o xtrace


export PR_NAME="PR-${1}"

function remove_website_code(){
	rm -fr /home/csss/${PR_NAME} || true
}

function remove_nginx_config(){
	rm -fr /home/csss/branch_${PR_NAME} || true
	cat /home/csss/nginx_site_config branch_* | sudo tee /etc/nginx/sites-available/PR_sites
	echo "}" | sudo tee -a /etc/nginx/sites-available/PR_sites
	sudo nginx -t
	sudo systemctl restart nginx
}

function remove_gunicorn_systemd_files(){
	gunicorn_socket="gunicorn_${PR_NAME}.socket"
	gunicorn="gunicorn_${PR_NAME}.service"

	sudo systemctl stop "${gunicorn_socket}"
	sudo systemctl disable "${gunicorn_socket}"

	sudo systemctl stop "${gunicorn}"
	sudo systemctl disable "${gunicorn}"

	sudo rm /etc/systemd/system/"${gunicorn_socket}"
	sudo rm /etc/systemd/system/"${gunicorn}"

	sudo systemctl daemon-reload
}

function remove_database(){
	docker exec csss_site_db_dev psql -U postgres -d postgres -c "DROP DATABASE \"${PR_NAME}\";" || true

}
remove_website_code

remove_nginx_config

remove_gunicorn_systemd_files

remove_database
