from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox
import base64
import datetime
from csss.oauth2 import RefreshToken

def access_token_refresher():
  print("access_token_refresher")
  now = ''
  try:
    file_object  = open("LAST_OAUTH2_TOKEN_REFRESH", "r") 
    last_update = file_object.readline()
    #todate=$(date +"%Y%m%d%H%M%S%N")
    #cond=$(date +"%Y%m%d%H%M%S%N")
    #todate=$(date +"%Y%m%d%H")
    #cond=$(date +"%Y%m%d%H")
    now = datetime.datetime.now().strftime("%Y%m%d%H")
    if (last_update is not now):
      access_token = RefreshToken(client_id, client_secret, refresh_token)
      file_object.close()
  except OSError as e:
    print("LAST_OAUTH2_TOKEN_REFRESH file was not found")
  finally:
    file_object  = open("LAST_OAUTH2_TOKEN_REFRESH", "w")
    file_object.write(now)
    file_object.close()


def extract_sender(from_header):
  indexOfFirst=from_header.index("<")
  print(from_header[0:indexOfFirst])
  return from_header[0:indexOfFirst]

def extract_body(decoded_body):
  indexOfFirst=decoded_body.index("UTF-8")
  indexOfLast = decoded_body.index("Content-Type: text/html")
  return decoded_body[indexOfFirst+8:indexOfLast-32].replace('\\n', '\n')


def index(request):
  print("announcements index")
  access_token_refresher()
  messages = Message.objects.all().order_by('-id')
  theMessage = Message.objects.all().order_by('id')
  for message in messages:
    decoded_body= str(base64.b64decode(message.body))
    message.from_header = extract_sender(message.from_header)
    message.body = extract_body(decoded_body)
  return render(request, 'announcements/announcements.html', {'messages': messages})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})