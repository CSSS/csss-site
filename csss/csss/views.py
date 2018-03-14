from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox

def index(request):
  print("announcements-index")
  object_list = Post.objects.all()
  print("1")
  messages = Message.objects.all()
  print("messages=[",end='')
  print(messages,end='')
  print("]")
  for message in messages:
    print('Received Subject=['+str(message.subject)+'] From=['+str(message.from_header)+'] From=['+str(message.from_address)+'] Body=['+str(message.body)+']')
  return render(request, 'announcements/announcements.html', {'object_list': object_list})
#	return render(request, 'announcements/announcements.html', {'content':['Hi you doiiiiiin?']})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
