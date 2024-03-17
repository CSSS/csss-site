#!/bin/bash

cd /home/csss;
. envCSSS/bin/activate;
. ./set_env.sh csss_site_envs/csss_site_gunicorn.env;
cd csss-site;
python manage.py nag_election_officer_share_results;