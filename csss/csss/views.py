from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox
import base64

def index(request):
  print("announcements-index")
  object_list = Post.objects.all()
  print("1")
  messages = Message.objects.all().order_by('-id')
  print("messages=[",end='')
  print(messages,end='')
  print("]")
  for message in messages:
    decoded_body= str(base64.b64decode(message.body))
    print("decoded_body=[",end='')
    print(decoded_body,end='')
    print("]")
    indexOfFirst=decoded_body.index("UTF-8")
    indexOfLast = decoded_body.index("Content-Type: text/html")
    print("indexOfFirst=["+str(indexOfFirst)+"] indexOfLast+["+str(indexOfLast)+"] -- indexOfFirst-indexOfLast=["+str(indexOfFirst-indexOfLast)+"] -- length=["+str(len(decoded_body))+"]")
    print(decoded_body[indexOfFirst+8:indexOfLast].replace('\\n', '\n'))
    message.body=decoded_body[indexOfFirst+8:indexOfLast-32].replace('\\n', '\n')
    print('Received Subject=['+str(message.subject)+'] From=['+str(message.from_header)+'] From=['+str(message.from_address)+'] Body=['+str(message.body)+']')
  return render(request, 'announcements/announcements.html', {'messages': messages})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
