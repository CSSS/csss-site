How the CSSS Site version 3 was set up   
  
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
  
## access token and gmail for dango-mailbox  
I am currently testing the usefulness of django-mailbox module to be able to recieve emails at the django site.  
Unfortunately, that module doesnt actually store the credentials itself and instead relies on [python-social-auth](https://github.com/python-social-auth) for credentials. THis is unfortunate because the documentation for that module is complicated as hell and I am not currently able to make heads or tails of how to utilize it for the csss-site.  
  
However, I have come up with an extremely hacky-solution of allowing the site to retrieve emails, involves modifying `/usr/local/lib/python3.5/dist-packages/django_mailbox/transports/gmail.py` which I strongly suspect is not a good thing, modfying source files for a module but thats just how it currently is being done.  
  
Modifications are outlined here  
  
```shell
    def _connect_oauth(self, username):
        # username should be an email address that has already been authorized
        # for gmail access
        try:
            from django_mailbox.google_utils import (
                get_google_access_token,
                fetch_user_info,
                AccessTokenNotFound,
            )
        except ImportError:
            raise ValueError(
                "Install python-social-auth to use oauth2 auth for gmail"
            )
        access_token = None
        while access_token is None:
            try:
#                access_token = get_google_access_token(username)
                access_token = '#######################################################' <-- hard_corded acccess token **NOT GOOD PRACTICE**
                google_email_address = 'csss.website@gmail.com' <-- hard_coded gmail **NOT GOOD PRACTICE**
#                google_email_address = fetch_user_info(username)['email']
            except TypeError:
                # This means that the google process took too long
                # Trying again is the right thing to do
                pass
            except AccessTokenNotFound:
                raise ValueError(
                    "No Token available in python-social-auth for %s" % (
                        username
                    )
                )
```