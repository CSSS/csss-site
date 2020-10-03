#!/bin/bash

set -e -o xtrace

rm csss-site/src/about/fixtures/* || true
rm csss-site/src/announcements/fixtures/* || true
rm csss-site/src/announcements/fixtures/* || true
rm csss-site/src/elections/fixtures/* || true
rm csss-site/src/resource_management/fixtures/* || true

scp "CI/refresh_fixtures/2_create_fixture_jsons.sh" csss@sfucsss.org:"/home/csss/create_jsons.sh"
ssh csss@sfucsss.org "/home/csss/create_jsons.sh"
scp -r csss@sfucsss.org:"/home/csss/csss-site/csss-site/src/*.json" .
ssh csss@sfucsss.org "rm -fr /home/csss/csss-site/csss-site/src/*.json"
ssh csss@sfucsss.org "rm /home/csss/create_jsons.sh"

mv about.json csss-site/src/about/fixtures/.
python CI/refresh_fixtures/sanitize_officer_info.py
mv announcements.json csss-site/src/announcements/fixtures/.
mv django_mailbox.json csss-site/src/announcements/fixtures/.
mv elections.json csss-site/src/elections/fixtures/.
mv resource_management.json csss-site/src/resource_management/fixtures/.

