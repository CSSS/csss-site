from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox
import base64

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
  messages = Message.objects.all().order_by('-id')
  theMessage = Message.objects.all().order_by('id')
  for message in messages:
    decoded_body= str(base64.b64decode(message.body))
    message.from_header = extract_sender(message.from_header)
    decoded_body = extract_body(decoded_body)
  return render(request, 'announcements/announcements.html', {'messages': messages})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})