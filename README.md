# csss-site-in-dev

In active development on Jace Manshadi's personal AWS account.

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