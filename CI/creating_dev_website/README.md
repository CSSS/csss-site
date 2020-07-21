# creating dev website

the "dev" website mainly exists to provide a database that all the other test websites at dev.sfucsss.org can copy their database from.

to setup the deb website that the other test websites copy from:

`#` -> run on prod server  
`:` -> run locally  
`$` -> on test server  

 2. `# docker exec -it csss_site_db ash`
 3. `# pg_dump -U postgres postgres -t about_term -t about_officer \
    -t about_announcementemailaddress -t elections_nominationpage \
    -t elections_nominee --data-only > backup.sql`
 4. `# exit`
 5. `# docker cp csss_site_db:/backup.sql backup.sql`
 6. `# scp backup.sql csss@dev.sfucsss.org:/home/csss/.`
 6.  `: ./CI/creating_dev_website/create_dev_on_server.sh -h`
 7. `$ docker cp backup.sql csss_site_db_dev:/backup.sql`
 8. `$ docker exec -it csss_site_db_dev ash`
 9. `$ psql -U postgres dev < backup.sql`
 5. Go to `dev.sfucsss.org/dev/admin` and log on
 6. Delete all the current email messages and then correct the email mailbox to point to the test inbox and download all the messages from that inbox.
 7. Delete all the things under Documents except for Repo and then re-do the git pull
