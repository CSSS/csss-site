#!/bin/bash

cd /home/csss;
. envCSSS/bin/activate;
. ./set_env.sh csss_site_envs/csss_site_gunicorn.env;
cd csss-site;
python manage.py remind_election_officer_to_provide_websurvey_link;