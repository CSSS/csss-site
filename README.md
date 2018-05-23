# csss-site-in-dev

In active development on Jace Manshadi's personal AWS account.
### Table of Contents
 - [Basic Instructions for Site set-up](#basic-instructions-for-site-set-up)
 - [Miscellanious/Extra References](#miscellaniousextra-references)
    - [Interacting with SQLite database](#interacting-with-sqlite-database)
        - [SQLite3 Commands](#sqlite3-commands)
        - [Script for SQLite3 Commands](#script-for-sqlite3-commands)
        - [Migrate Models](#migrate-models)
    - [Location of model where emails are stored](#location-of-model-where-emails-are-stored)
    - [Django-mailbox](#django-mailbox)

## Basic Instructions for Site set-up

How the CSSS Site version 3 is being set up   
  
By: Jace Manshadi  
Position: Webmaster Summer 2017 - Present  
contact: j_manshad@sfu.ca  
  
The site was set up with help from YouTube tutorial: https://www.youtube.com/playlist?list=PLQVvvaa0QuDeA05ZouE4OzDYLHY-XH-Nd   
  
Also avaiable here: https://pythonprogramming.net/django-web-development-with-python-intro/  
  
These instructions were carried out on a VM on AWS with the Ubuntu 16.04 O.S.  
  
```shell
ssh -i csssWebsiteKeyPair.pem ubuntu@ec2-52-91-226-24.compute-1.amazonaws.com  
sudo apt install python3-pip  
python3.5 -m pip install -U pip  
python3.5 -m pip install -r requirements.txt  
mkdir csss_website  
cd csss_website/  
django-admin startproject csss  
```
made following commit:  
add following host to settings.py  
        ALLOWED_HOSTS = ['ec2-52-91-226-24.compute-1.amazonaws.com']  
```shell
python3.5 manage.py runserver 172.31.17.191:8000  
python3.5 manage.py startapp webapp  
python3.5 manage.py startapp personal  
```

## Miscellanious/Extra References

***************************************
### Interacting with SQLite database
***************************************

#### SQLite3 Commands

```shell
$ cd csss_website/csss/
$ sqlite3 db.sqlite3

sql commands

sqlite> .tables
sqlite> PRAGMA table_info(django_mailbox_message);
sqlite> SELECT body FROM django_mailbox_message WHERE id == 7;
sqlite> SELECT * FROM django_mailbox_message ;
sqlite> SELECT subject FROM django_mailbox_message;
sqlite> SELECT from_header FROM django_mailbox_message;
sqlite> SELECT to_header FROM django_mailbox_message;
sqlite> SELECT body FROM django_mailbox_message;
sqlite> SELECT body FROM django_mailbox_message WHERE id == 1;
```

#### Script for SQLite3 Commands

```shell
#!/bin/bash

sqlite3 db.sqlite3 <<EOF
.tables
PRAGMA table_info(django_mailbox_message);
EOF
```

#### Migrate Models

```shell
python3.5 manage.py makemigrations announcements
python3.5 manage.py migrate
```

*************************************************
### Location of model where emails are stored
*************************************************
(`django-mailbox/django-mailbox/models.py`)

*******************
### django-mailbox
*******************
[Django-Mailbox Docu](http://django-mailbox.readthedocs.io/en/latest/)  
[Djanho-Mailbox Mailbox-Types](http://django-mailbox.readthedocs.io/en/latest/topics/mailbox_types.html)  
[Django-Mailbox Repo](https://github.com/coddingtonbear/django-mailbox)  
