#!/bin/bash

set -e -o xtrace

. ~/set_env.sh site_envs_django_admin
. ~/envCSSS/bin/activate
cd ~/csss-site/

python3 manage.py dumpdata about --indent 4 --output about.json
python3 manage.py dumpdata announcements --indent 4 --output announcements.json
python3 manage.py dumpdata django_mailbox --indent 4 --output django_mailbox.json
#python3 manage.py dumpdata elections --indent 4 --output elections.json
python3 manage.py dumpdata auth.group --indent 4 --output auth.json
python3 manage.py dumpdata resource_management.officerpositiongithubteam resource_management.officerpositiongithubteammapping --indent 4 --output resource_management.json
