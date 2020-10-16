#!/bin/bash

set -e -o xtrace

rm csss-site/src/about/fixtures/* || true
rm csss-site/src/announcements/fixtures/* || true
rm csss-site/src/announcements/fixtures/* || true
rm csss-site/src/elections/fixtures/* || true
rm csss-site/src/resource_management/fixtures/* || true

scp "CI/refresh_fixtures/2_create_fixture_jsons.sh" csss@sfucsss.org:"/home/csss/create_jsons.sh"
ssh csss@sfucsss.org "/home/csss/create_jsons.sh"
scp -r csss@sfucsss.org:"/home/csss/csss-site/*.json" .
ssh csss@sfucsss.org "rm -fr /home/csss/csss-site/*.json"
ssh csss@sfucsss.org "rm /home/csss/create_jsons.sh"

mv about.json csss-site/src/about/fixtures/.
# ugly blob of jq obtained from https://stackoverflow.com/a/64181110/7734535
# just aiming to cleans the bios from any sensitive info about the officers so their information
# is not leaked in the staging environnment
jq ' map( reduce ("sfuid", "sfu_email_alias", "github_username", "gmail") as $k (.; if .fields[$k] then .fields[$k] = $k else . end) | if .fields.phone_number then .fields.phone_number = 0 else . end )' \
csss-site/src/about/fixtures/about.json  > csss-site/src/about/fixtures/temp_about.json
mv csss-site/src/about/fixtures/temp_about.json csss-site/src/about/fixtures/about.json
mv announcements.json csss-site/src/announcements/fixtures/.
mv django_mailbox.json csss-site/src/announcements/fixtures/.
mv elections.json csss-site/src/elections/fixtures/.
mv resource_management.json csss-site/src/resource_management/fixtures/.

