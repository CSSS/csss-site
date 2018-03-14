from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import Mailbox
from django.core.management.base import BaseCommand
import logging
logger = logging.getLogger(__name__)

def index(request):
  print("announcements-index")
  object_list = Post.objects.all()
  print("1")
  mailboxes = Mailbox.active_mailboxes.all()
  print("mailboxes=[",end='')
  print(mailboxes,end='')
  print("]")
  for mailbox in mailboxes:
    print('Gathering messages for %s',mailbox.name)
    messages = mailbox.get_new_mail()
  print("messages=[",end='')
  print(messages,end='')
  print("]")
  for message in messages:
    print('Received Subject=[%s] From=[%s] From=[%s] Body=[%s]',message.subject,message.from_header,message.from_address,message.body)
  return render(request, 'announcements/announcements.html', {'object_list': object_list})
#	return render(request, 'announcements/announcements.html', {'content':['Hi you doiiiiiin?']})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
