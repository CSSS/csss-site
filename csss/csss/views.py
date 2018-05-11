from django.shortcuts import render
from announcements.models import Post, AnnouncementAttachment
import announcements
from django_mailbox.models import MessageAttachment, Message, Mailbox
from django_mailbox import admin
import base64
import datetime
import six
from time import strptime
from pytz import timezone

def filterSender(messages):
  theBody=""
  valid_messages = []
  valid_senders = []
  with open("csss/poster.txt", "r") as file:
    for line in file:
      valid_senders.append(line.rstrip().lower())

  for message in messages:
    from_header = str(message.from_header.rstrip())
    for sender in valid_senders:
      if sender in from_header:
        valid_messages.append(message)
        break
  
  return valid_messages;

def extract_date(decoded_date):
  rev = decoded_date[::-1]
  revIndexOfPDT=rev.index(")TDP(")
  revIndexOfLast=rev.find(" ",revIndexOfPDT+9)
  revIndexOfFirst=rev.find(" ",revIndexOfLast+1)
  for x in range(4):
    revIndexOfFirst=rev.find(" ",revIndexOfFirst+1)
  indexOfFirst=len(decoded_date)-revIndexOfFirst-1
  indexOfLast=len(decoded_date)-revIndexOfLast-1
  return decoded_date[indexOfFirst+1:indexOfLast]

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

def combine_announcements ( messages, posts):
  final_posts = []
  messageIndex = 0
  postIndex = 0
  while len(messages) > messageIndex and len(posts) > postIndex:
    if messages[messageIndex].processed < posts[postIndex].processed:
      final_posts.append(posts[postIndex])
      postIndex=postIndex+1
    else:
      final_posts.append(messages[messageIndex])
      messageIndex=messageIndex+1

  if len(posts) > postIndex:
    for x in range(postIndex, len(posts)):
      final_posts.append(posts[x])

  if len(messages) > messageIndex:
    for x in range(messageIndex, len(messages)):
      final_posts.append(messages[x])

  return final_posts

def convert_email_datetime_string_to_naive_datetime_object(date_from_email):
  indexBeforeDate = date_from_email.find(" ", 1)
  indexAfterDay = date_from_email.find(" ", indexBeforeDate+ 1)
  day = int(date_from_email[indexBeforeDate+1:indexAfterDay])
  
  indexAfterMonth = date_from_email.find(" ", indexAfterDay +1)
  month = date_from_email[indexAfterDay+1:indexAfterMonth]
  month = int(strptime(month,'%b').tm_mon)
  
  indexAfterYear = date_from_email.find(" ", indexAfterMonth + 1)
  year = int(date_from_email[indexAfterMonth+1:indexAfterYear])

  indexAfterHour = date_from_email.find(":", indexAfterYear + 1)
  hour = int(date_from_email[indexAfterYear+1:indexAfterHour])

  indexAfterMinute = date_from_email.find(":", indexAfterHour + 1)
  minute = int(date_from_email[indexAfterHour+1:indexAfterMinute])

  second = int(date_from_email[indexAfterMinute+1:])

  return datetime.datetime(year, month, day, hour, minute, second)

def removePhotoEmails(message):
  if "Subject: [WEBSITE PHOTOS]" in str(message):
    print("email is for the photo gallery")
    return True
  else:
    print("email is for the announcements")
    return False

def index(request):
  print("announcements index")
  admin.get_new_mail(condition=removePhotoEmails)
  messages = Message.objects.all().order_by('-id')
  attachments = MessageAttachment.objects.all().order_by('-id')
  messages = filterSender(messages)
  for message in messages:

    #will modify the processed date to be change from the day the mailbox was polled to the date the email was sent
    message.processed=convert_email_datetime_string_to_naive_datetime_object(str(extract_date(str(base64.b64decode(message.body)))))
    
    #exracting the snder from the from_header field
    message.from_header = extract_sender(message.from_header)

    #decoding the email body
    message.body = get_body_from_message(message.get_email_object(), 'text', 'html').replace('\n', '').strip().replace("align=center", "")
  posts = []
  for post in Post.objects.all().order_by('-id'):
    posts.append(post)

  final_posts = combine_announcements(messages, posts)

  return render(request, 'announcements/announcements.html', {'final_posts': final_posts, 'attachments': attachments})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
