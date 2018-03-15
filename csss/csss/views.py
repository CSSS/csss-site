from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox
import base64

def extract_sender(from_header):
  indexOfFirst=from_header.index("<")
  return from_header[0:indexOfFirst]

def extract_body(email_body):
  indexOfFirst=email_body.index("UTF-8")
  indexOfLast = email_body.index("Content-Type: text/html")
  return decoded_body[indexOfFirst+8:indexOfLast-32].replace('\\n', '\n')


def index(request):
  print("announcements index")
  messages = Message.objects.all().order_by('-id')
  print (type(messages))
  for message in messages:
    decoded_body= str(base64.b64decode(message.body))
    sender = extract_sender(message.from_header)
    body_of_email = extract_body(message.body)
  return render(request, 'announcements/announcements.html', {'messages': messages})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})