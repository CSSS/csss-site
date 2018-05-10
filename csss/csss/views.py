from django.shortcuts import render
from announcements.models import Post
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox
import base64
import datetime
import six

def extract_sender(from_header):
  indexOfFirst=from_header.index("<")
  return from_header[0:indexOfFirst]


def get_body_from_message(message, maintype, subtype):
    """
    Fetchs the body message matching main/sub content type.
    """
    body = six.text_type('')
    for part in message.walk():
        if part.get('content-disposition', '').startswith('attachment;'):
            continue
        if part.get_content_maintype() == maintype and \
                part.get_content_subtype() == subtype:
            charset = part.get_content_charset()
            this_part = part.get_payload(decode=True)
            if charset:
                try:
                    this_part = this_part.decode(charset, 'replace')
                except LookupError:
                    this_part = this_part.decode('ascii', 'replace')
                    logger.warning(
                        'Unknown encoding %s encountered while decoding '
                        'text payload.  Interpreting as ASCII with '
                        'replacement, but some data may not be '
                        'represented as the sender intended.',
                        charset
                    )
                except ValueError:
                    this_part = this_part.decode('ascii', 'replace')
                    logger.warning(
                        'Error encountered while decoding text '
                        'payload from an incorrectly-constructed '
                        'e-mail; payload was converted to ASCII with '
                        'replacement, but some data may not be '
                        'represented as the sender intended.'
                    )
            else:
                this_part = this_part.decode('ascii', 'replace')

            body += this_part

    return body



def extract_body(decoded_date):
  rev = decoded_date[::-1]
  revIndexOfPDT=rev.index(")TDP(")
  revIndexOfLast=rev.find(" ",revIndexOfPDT+9)
  revIndexOfFirst=rev.find(" ",revIndexOfLast+1)
  for x in range(4):
    revIndexOfFirst=rev.find(" ",revIndexOfFirst+1)
  indexOfFirst=len(decoded_date)-revIndexOfFirst-1
  indexOfLast=len(decoded_date)-revIndexOfLast-1
  return decoded_date[indexOfFirst+1:indexOfLast]

def filterSender(messages):
  theBody=""
  final_messages = []
  for message in messages:
    include=0
    print("\n\nmessage.from_header=["+str(message.from_header)+"]")
    file_object  = open("csss/poster.txt", "r")
    for line in file_object:
      line = str(line.rstrip())
      from_header = str(message.from_header.rstrip())
      print("\tline=["+line+"]")
      if ( line in from_header):
        print("["+line+"] detected in ["+from_header+"]")
        include=include+1
    print("include="+str(include))
    if (include > 0):
      final_messages.append(message)
      print("message not being excluded=["+str(message.subject)+"]")
    else:
      message.body=''
      print("message being excluded=["+str(message.subject)+"]")
    file_object.close()
  for message in final_messages:
    print("\n\nbody for message from "+message.from_header+":")
    print("\tbody=["+message.body+"]")
  
  #final_messages = messages.exclude(body='')
  print("final_messages=["+str(final_messages)+"]")
  return final_messages;


def index(request):
  print("announcements index")
  file_object = open("csss/poster.txt", "r")
  messages = Message.objects.all().order_by('-id')
  print("messages datatype= "+str(type(messages)))
  attachments = MessageAttachment.objects.all().order_by('-id')
  messages = filterSender(messages)
  #print("attachments="+str(attachments))
  for message in messages:
    #print("message="+str(message.id))
    original_body = str(base64.b64decode(message.body))
    message.processed=str(extract_body(original_body))
    decoded_body = get_body_from_message(message.get_email_object(), 'text', 'html').replace('\n', '').strip()
    #decoded_body= str(base64.b64decode(message.body))
    message.from_header = extract_sender(message.from_header)
    decoded_body = decoded_body.replace("align=center", "")
    message.body = decoded_body
    #message.body = extract_body(decoded_body)

  return render(request, 'announcements/announcements.html', {'messages': messages, 'attachments': attachments})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
