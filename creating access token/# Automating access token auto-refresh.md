# Automating access token auto-refresh

`sudo find / -name django_mailbox` to locate the location of the module

add the file gmail-1 and gmail-2 to the transports folder under the django_mailbox folder

add the following line to crontab using `crontab -e`

`sudo -H python3.5 /home/ubuntu/csss_website/access_token_refresher.py`

correct the paths of gmail.py, gmail-1 and gmail-2 in access_token_refresher.py

run the command `wget <oauth2.py_path>` inside of the top csss_website. You can determine the path from [this repo wiki](https://github.com/google/gmail-oauth2-tools/wiki/OAuth2DotPyRunThrough)