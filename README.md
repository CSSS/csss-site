# csss-site-in-dev

In active development on the CSSS Digital Ocean Account
### Table of Contents
 - [Basic Instructions for Site creation](#basic-instructions-that-were-used-for-site-creation)
 - [Basic instructions for site set-up](#basic-instructions-for-site-set-up)
 - [Miscellanious/Extra References](#miscellaniousextra-references)
    - [mailbox uri to add to django_mailbox inside of CMS](#mailbox-uri-to-add-to-django_mailbox-inside-of-cms)
    - [Interacting with SQLite database](#interacting-with-sqlite-database)
        - [SQLite3 Commands](#sqlite3-commands)
        - [Script for SQLite3 Commands](#script-for-sqlite3-commands)
        - [Migrate Models](#migrate-models)
    - [Location of model where emails are stored](#location-of-model-where-emails-are-stored)
    - [Django-mailbox](#django-mailbox)
    - [Determining what process is using a port](#determing-what-process-is-using-a-port)
    - [Google Links to allow a gmail to be used with django-mailbox](#google-links-to-allow-a-gmail-to-be-used-with-django-mailbox)

## Basic Instructions that were used for Site creation

How the CSSS Site version 3 is being set up   
  
By: Jace Manshadi  
Position: Webmaster Summer 2017 - Present  
contact: j_manshad@sfu.ca  
  
The site was set up with help from YouTube tutorial: https://www.youtube.com/playlist?list=PLQVvvaa0QuDeA05ZouE4OzDYLHY-XH-Nd   
  
Also avaiable here: https://pythonprogramming.net/django-web-development-with-python-intro/  
  
These instructions were carried out on a VM on AWS with the Ubuntu 16.04 O.S.  
  
```shell
sudo apt install python3 python3-pip  
python3.5 -m pip install -U pip  
python3.5 -m pip install -r requirements.txt  
mkdir csss_website  
cd csss_website/  
django-admin startproject csss  
```

```shell
python3.5 manage.py startapp webapp  
python3.5 manage.py startapp personal  
python3.5 manage.py runserver 0.0.0.0:8000  

```
## Basic instructions for Site Set-up
```shell
git clone https://github.com/CSSS/csss-site-in-dev.git
cd csss-site-in-dev/
sudo apt-get install -y python3 python3-pip
python3.6 -m pip install -U pip
python3.6 -m pip install --upgrade pip
sudo -H python3.6 -m pip install virtualenv
virtualenv ENV
. ENV/bin/activate
python3.6 -m pip install -r requirements.txt
export ip_addr='46.101.225.142'
cd csss
python3.6 manage.py createsuperuser
python3.6 manage.py runserver 0.0.0.0:8000

#running site on a VM, the IP speciifed below is the private IP of the server
python3.5 manage.py runserver 0.0.0.0:8000

#running site on localhost
python3.5 manage.py runserver 8000
```

## Miscellanious/Extra References

***************************************
### mailbox uri to add to django_mailbox inside of CMS
***************************************

(`gmail+ssl://csss.website%40gmail.com:<password>@imap.gmail.com?processed=processed`)

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
  
******************
### Determing what process is using a port
******************
```shell
sudo lsof -n -i :<portNumber>
```
  
**********************  
### Bootstrap Stuff **  
**********************  
https://getbootstrap.com/docs/3.3/javascript/#tabs  
https://getbootstrap.com/docs/3.3/javascript/  
https://getbootstrap.com/docs/3.3/components/#nav-dropdowns  

*****************************************************************
### Google Links to allow a gmail to be used with django-mailbox
*****************************************************************

- [Use IMAP to check Gmail on other email clients](https://support.google.com/mail/answer/7126229?visit_id=1-636603205765509733-1797557889&rd=2#cantsignin)
- [Let less secure apps access your account](https://support.google.com/accounts/answer/6010255)
  - [Allow less secure apps to access your account](https://myaccount.google.com/lesssecureapps)
