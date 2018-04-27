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



def extract_body(decoded_body):
  indexOfFirst=decoded_body.index("UTF-8")
  indexOfLast = decoded_body.index("Content-Type: text/html")
  return decoded_body[indexOfFirst+8:indexOfLast-32].replace('\\n', '\n')




def index(request):
  print("announcements index")
  messages = Message.objects.all().order_by('-id')
  attachments = MessageAttachment.objects.all().order_by('-id')
  #print("attachments="+str(attachments))
  for message in messages:
    #print("message="+str(message.id))
    decoded_body = get_body_from_message(message.get_email_object(), 'text', 'html').replace('\n', '').strip()
    #decoded_body= str(base64.b64decode(message.body))
    message.from_header = extract_sender(message.from_header)
    decoded_body = decoded_body.replace("align=center", "")
    message.body = decoded_body
    #message.body = extract_body(decoded_body)

  return render(request, 'announcements/announcements.html', {'messages': messages})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
