#!/bin/bash

cd ~/
. set_env.sh site_envs_django_admin
. envCSSS/bin/activate
cd csss-site
python3.8 manage.py dumpdata --output temp_website_prod_backup.json
jq . temp_website_prod_backup.json > website_prod_backup.json
rm temp_website_prod_backup.json
scp website_prod_backup.json  csss@fraser.sfu.ca:/home/csss/.
rm website_prod_backup.json