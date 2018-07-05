# csss-site-in-dev

In active development on Jace Manshadi's personal AWS account.
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
add following host to settings.py  
        ALLOWED_HOSTS = ['ec2-52-91-226-24.compute-1.amazonaws.com']  
```shell
python3.5 manage.py startapp webapp  
python3.5 manage.py startapp personal  
python3.5 manage.py runserver 172.31.17.191:8000  

```
## Basic instructions for Site Set-up
```shell
git clone https://github.com/CSSS/csss-site-in-dev.git
sudo apt-get install -y python3-pip
python3.5 -m pip install -U pip
python3.5 -m pip install --upgrade pip
python3.5 -m pip install -r requirements.txt
cd csss

#running site on a VM, the IP speciifed below is the private IP of the server
python3.5 manage.py runserver 172.31.17.191:8000

#running site on localhost
python3.5 manage.py runserver 8000
```
  
### Setting up Sublime Text and X11 Forwarding on server  
  
#### Sublime  
[Link for Commands to install sublime via commandline](http://tipsonubuntu.com/2017/05/30/install-sublime-text-3-ubuntu-16-04-official-way/)  
```shell
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text
```
  
#### X11 Forwarding  
[First Link for commmands to set up X11 Forwarding](https://askubuntu.com/a/213685)  
[Second Link for commmands to set up X11 Forwarding](https://askubuntu.com/a/718087)  
```shell
sudo apt-get install -y xorg openbox libgtk2.0-0 libgdk-pixbuf2.0-0 libfontconfig1 libxrender1 libx11-6 libglib2.0-0  libxft2 libfreetype6 libc6 zlib1g libpng12-0 libstdc++6-4.8-dbg-arm64-cross libgcc1 
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
*****************************************************************
### Google Links to allow a gmail to be used with django-mailbox
*****************************************************************

- [Use IMAP to check Gmail on other email clients](https://support.google.com/mail/answer/7126229?visit_id=1-636603205765509733-1797557889&rd=2#cantsignin)
- [Let less secure apps access your account](https://support.google.com/accounts/answer/6010255)
  - [Allow less secure apps to access your account](https://myaccount.google.com/lesssecureapps)