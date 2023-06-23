#!/bin/bash

cd /home/csss;
. envCSSS/bin/activate;
. ./set_env.sh site_envs/site_envs_gunicorn;
cd csss-site;
python manage.py validate_google_workspace_shared_team_drive_for_deep_exec;