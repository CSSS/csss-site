#!/bin/bash

cd /home/csss/
. csssENV/bin/activate
cd csss-site-in-dev/csss/
python3.7 manage.py getmail
deactivate
