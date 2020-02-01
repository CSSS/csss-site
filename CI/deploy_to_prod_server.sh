#!/bin/bash

set -e -o xtrace

# remove all old and replace with newer code. will make sure that the migrations are not deleted as they need to be
# persistent through the changes
ssh csss@sfucsss.org "find /home/csss/csss-site/csss-site/src -mindepth 1 ! -regex '.*migrations.*' -delete" || true
ssh csss@sfucsss.org "mkdir -p /home/csss/csss-site/csss-site/src"
scp -r "csss-site/src"/* csss@sfucsss.org:/home/csss/csss-site/csss-site/src/

# transfer requirements file and script that is used to setup the website
scp -r "requirements.txt" csss@sfucsss.org:/home/csss/csss-site/requirements.txt
scp -r "CI/deploy_changes.sh" csss@sfucsss.org:/home/csss/deploy_changes.sh

ssh csss@sfucsss.org "/home/csss/deploy_changes.sh"
