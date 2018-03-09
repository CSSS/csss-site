# Steps for Generating Access Token for gmail inbox
  
## Creating Developer Project and AccessToken using csss.website account  
https://console.developers.google.com/apis/dashboard  
Create Project  
![Create Project](Create_Project.png)  
Select GMAIL API  
![Select GMAIL API](Select%20GMAIL%20API.png)  
Enable GMAIL API  
![Enable GMAIL API](Enable%20GMAIL%20API.png)  
Create Credentials  
![Create Credentials](Create%20Credentials.png)  
Creating client ID  
![Creating client ID](Creating%20client%20ID.png)  
Configure Consent Screen  
![Configure Consent Screen](Configure%20Consent%20Screen.png)  
Creating OAuth consent screen  
![Creating OAuth consent screen](Creating%20Cconsent%20screen.png)  
Selecting client ID Application Type  
![Selecting client ID Application Type](Selecting%20client%20ID%20Application%20Type.png)  
Copy Client ID and client secret  
![Copy Client ID and client secret](Copy%20Client%20ID%20and%20client%20secret.png)  
  
## Instructions for ouath2.py script  
```shell
wget https://raw.githubusercontent.com/google/gmail-oauth2-tools/master/python/oauth2.py
```