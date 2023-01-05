#!/bin/bash

cd /home/csss;
. envCSSS/bin/activate;
. ./set_env.sh site_envs/site_envs_gunicorn;
cd csss-site;
python manage.py nag_officers_to_enter_info;