#!/bin/bash

function help(){
	echo "Mandatory arguments"
	echo -e "\t-website_secret_key"
	echo -e "\t-db_password"
	echo "Optional arguments"
	echo -e "\t-branch_name"
	echo -e "\t-stripe_publishable_key"
	echo -e "\t-stripe_secret_key"
	exit 0
}
while [ "$#" -gt 0 ]
do
	if [ "${1}" = "-branch_name" ]; then
		export BRANCH_NAME="${2}"
		shift
		shift
	elif [ "${1}" = "-website_secret_key" ]; then
		export WEBSITE_SECRET_KEY="${2}"
		shift
		shift
	elif [ "${1}" = "-db_password" ]; then
		export DB_PASSWORD="${2}"
		shift
		shift
	elif [ "${1}" = "-stripe_publishable_key" ]; then
		export STRIPE_PUBLISHABLE_KEY="${2}"
		shift
		shift
	elif [ "${1}" = "-stripe_secret_key" ]; then
		export STRIPE_SECRET_KEY="${2}"
		shift
		shift
	elif [ "${1}" = "-h" ]; then
		help
	else
		echo -e "\nUnrecognized flag \"${1}\"\n"
		help
	fi
done

if [ -z $WEBSITE_SECRET_KEY ] || [ -z $DB_PASSWORD ]; then
	echo -e "\n\nplease specify the secret key and db password using following flags:"
	echo -e "\t-website_secret_key, -db_password\n\n"
	exit 1
fi
if [ -z $BRANCH_NAME ]; then
	echo "settings BRANCH_NAME to a default of \"dev\""
	export BRANCH_NAME="dev"
fi
echo "BRANCH_NAME=${BRANCH_NAME}"
echo "WEBSITE_SECRET_KEY=${WEBSITE_SECRET_KEY}"
echo "DB_PASSWORD=${DB_PASSWORD}"
echo "STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}"
echo "STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}"

export BASE_DIR="/home/csss/${BRANCH_NAME}";

export DEBUG=true;
export HOST_ADDRESS=dev.sfucsss.org;

./CI/validate_and_deploy/update_files_on_server.sh;
ssh csss@"${HOST_ADDRESS}" "/home/csss/${BRANCH_NAME}/deploy_changes.sh";
