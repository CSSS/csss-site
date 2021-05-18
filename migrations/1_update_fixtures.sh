#!/bin/bash

set -e -o xtrace

rm ../../migrations/fixtures/* || true

scp "../../migrations/0_create_fixture_jsons.sh" csss@sfucsss.org:"/home/csss/create_jsons.sh"
ssh csss@sfucsss.org "/home/csss/create_jsons.sh"
scp -r csss@sfucsss.org:"/home/csss/csss-site/*.json" .
ssh csss@sfucsss.org "rm -fr /home/csss/csss-site/*.json"
ssh csss@sfucsss.org "rm /home/csss/create_jsons.sh"

mv about.json ../../migrations/fixtures/.
python3 ../../migrations/update_confidential_info.py
mv auth.json ../../migrations/fixtures/.
mv announcements.json ../../migrations/fixtures/.
mv django_mailbox.json ../../migrations/fixtures/.
mv elections.json ../../migrations/fixtures/.
mv resource_management.json ../../migrations/fixtures/.