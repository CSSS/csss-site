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
mv announcements.json ../../migrations/fixtures/.
mv django_mailbox.json ../../migrations/fixtures/.
mv elections.json ../../migrations/fixtures/.
mv resource_management.json ../../migrations/fixtures/.

cd ../
rm -fr csss-site.git
git clone --mirror https://github.com/CSSS/csss-site.git
cd csss-site.git
java -jar /usr/bin/bfg-1.13.2.jar --delete-files about.json
java -jar /usr/bin/bfg-1.13.2.jar --delete-files announcements.json done
java -jar /usr/bin/bfg-1.13.2.jar --delete-files django_mailbox.json done
java -jar /usr/bin/bfg-1.13.2.jar --delete-files elections.json done
java -jar /usr/bin/bfg-1.13.2.jar --delete-files resource_management.json

git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push