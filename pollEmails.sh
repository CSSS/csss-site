#!/bin/bash

cd /home/csss/
. ENV/bin/activate
cd csss-site-in-dev/csss/
export ip_addr='$1'
python3.7 manage.py getmail
deactivate
