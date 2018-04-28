# csss-site-in-dev

In active development on Jace Manshadi's personal AWS account.
### Table of Contents
 - [Basic Instructions for Site set-up](#basic-instructions-for-site-set-up)
 - [Miscellanious/Extra References](#miscellaniousextra-references)
    - [Interacting with GMAIL database](#interacting-with-gmail-database)
    - [Location of model where emails are stored](#location-of-model-where-emails-are-stored)
    - [Python Social Auth](##python-social-auth)
    - [Django-mailbox](#django-mailbox)
    - [UPDATING MIGRATIONS FOR PYTHON-SOCIAL-AUTH](#updating-migrations-for-python-social-auth)
    - [Google Docu](#google-docu)

## Basic Instructions for Site set-up

How the CSSS Site version 3 is being set up   
  
By: Jace Manshadi  
Position: Webmaster Summer 2017 - Present  
contact: j_manshad@sfu.ca  
  
The site was set up with help from YouTube tutorial: https://www.youtube.com/playlist?list=PLQVvvaa0QuDeA05ZouE4OzDYLHY-XH-Nd   
  
Also avaiable here: https://pythonprogramming.net/django-web-development-with-python-intro/  
  
These instructions were carried out on a VM on AWS with the Ubuntu 16.04 O.S.  
  
ssh -i csssWebsiteKeyPair.pem ubuntu@ec2-52-91-226-24.compute-1.amazonaws.com  
sudo apt install python3-pip  
pip3 install -U pip  
pip3 install django  
mkdir csss_website  
cd csss_website/  
django-admin startproject csss  
made following commit:  
add following host to settings.py  
        ALLOWED_HOSTS = ['ec2-52-91-226-24.compute-1.amazonaws.com']  
python3.5 manage.py runserver 172.31.17.191:8000  
python3.5 manage.py startapp webapp  
python3.5 manage.py runserver 172.31.17.191:8000  
python3.5 manage.py startapp personal  
   
## Miscellanious/Extra References

***************************************
### Interacting with GMAIL database
***************************************
```
same command to interact with database
$ python3 manage.py dbshell
$ sqlite3 db.sqlite3

sql commands
sqlite> SELECT body FROM django_mailbox_message WHERE id == 7;
sqlite> SHOW * FROM django_mailbox_mailbox
sqlite> SELECT * FROM django_mailbox_mailbox ;
sqlite> SELECT * FROM django_mailbox_message ;
sqlite> .tables

sqlite> PRAGMA table_info(django_mailbox_message)
sqlite> SELECT subject FROM django_mailbox_message;
sqlite> SELECT from_header FROM django_mailbox_message;
sqlite> SELECT to_header FROM django_mailbox_message;
sqlite> SELECT body FROM django_mailbox_message;
sqlite> SELECT body FROM django_mailbox_message WHERE id == 1;
```

*************************************************
### Location of model where emails are stored
*************************************************
(`django-mailbox/django-mailbox/models.py`)

*******************
### django-mailbox
*******************
http://django-mailbox.readthedocs.io/en/latest/  
http://django-mailbox.readthedocs.io/en/latest/topics/mailbox_types.html#gmail-imap-with-oauth2-authentication  
http://django-mailbox.readthedocs.io/en/latest/topics/mailbox_types.html  
https://github.com/coddingtonbear/django-mailbox  
