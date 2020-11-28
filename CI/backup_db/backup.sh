#!/bin/bash

cd ~/
. set_env.sh site_envs_django_admin
. envCSSS/bin/activate
cd csss-site
python3.8 manage.py dumpdata --output website_prod_backup.json
scp website_prod_backup.json  csss@fraser.sfu.ca:/home/csss/.
rm website_prod_backup.json