#!/bin/bash

cd /home/csss;
. envCSSS/bin/activate;
. ./set_env.sh site_envs/site_envs_gunicorn;
cd csss-site;
python manage.py process_announcements --poll_email;