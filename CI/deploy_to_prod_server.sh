#!/bin/bash

set -e -o xtrace

# remove all old and replace with newer code. will make sure that the migrations are not deleted as they need to be
# persistent through the changes
ssh csss@sfucsss.org "find /home/csss/csss-site/csss-site/src -mindepth 1 ! -regex '.*migrations.*' -delete" || true
ssh csss@sfucsss.org "mkdir -p /home/csss/csss-site/csss-site/src"
scp -r "csss-site/src"/* csss@sfucsss.org:/home/csss/csss-site/csss-site/src/

# transfer requirements file and script that is used to setup the website
scp "requirements.txt" csss@sfucsss.org:/home/csss/csss-site/requirements.txt
scp "CI/deploy_changes.sh" csss@sfucsss.org:/home/csss/deploy_changes.sh

echo "BASE_DIR=${BASE_DIR}" > site_envs
echo "SECRET_KEY=${WEBSITE_SECRET_KEY}" >> site_envs
echo "DEBUG=${DEBUG}" >> site_envs
echo "HOST_ADDRESS=${HOST_ADDRESS}" >> site_envs
echo "DB_PASSWORD=${DB_PASSWORD}" >> site_envs
echo "STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}" >> site_envs
echo "STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}" >> site_envs

scp site_envs csss@sfucsss.org:/home/csss/site_envs
scp "CI/setEnv.sh" csss@sfucsss.org:/home/csss/setEnv.sh


ssh csss@sfucsss.org "/home/csss/deploy_changes.sh"
