from django.shortcuts import render
from email.utils import formatdate, parseaddr
from announcements.models import Post, AnnouncementAttachment
from about.models import Officer, Term, AnnouncementEmailAddress
import announcements
from django_mailbox.models import Message, Mailbox
import base64
import datetime
import six
from time import strptime
from pytz import timezone
import math

def index(request):
    print("announcements index")
    currentPage=request.GET.get('p', 'none')
    if currentPage == 'none':
        currentPage = 1
    else:
        currentPage=int(currentPage)

    request_path = request.path

    sfuEmails = [email.email for email in AnnouncementEmailAddress.objects.all()]
    print(f" sfuEmails {sfuEmails}")

    messages = Message.objects.all().order_by('-id')

    valid_messages = [message for message in messages if message.from_address[0] in sfuEmails]

    number_of_valid_messages = len(valid_messages)

    lowerBound = ( ( ( currentPage  - 1 ) * 5 ) + 1 )
    upperBound = currentPage * 5

    messages_to_display = []
    index=0
    for media in valid_messages:
        index+=1
        if ( lowerBound <= index ) and ( index <= upperBound ):
            messages_to_display.append(media)

    if currentPage == 1:
        previousPage = math.floor((number_of_valid_messages / 5 ) + 1)
        nextPage = 2
    elif currentPage == math.floor((number_of_valid_messages / 5 ) + 1):
        previousPage = currentPage - 1
        nextPage = 1
    else:
        previousPage = currentPage - 1
        nextPage = currentPage + 1

    previousButtonLink=request_path+'?p='+str(previousPage)
    nextButtonLink=request_path+'?p='+str(nextPage)

    for message in messages_to_display:
        #will modify the processed date to be change from the day the mailbox was polled to the date the email was sent
        try:
            dt = datetime.datetime.strptime(message.get_email_object().get('date'), '%a, %d %b %Y %H:%M:%S %z')
        except ValueError as e:
            dt = datetime.datetime.strptime(message.get_email_object().get('date')[:-6], '%a, %d %b %Y %H:%M:%S %z')
        message.processed = dt
        message.from_header = parseaddr(message.from_header)[0]


    for post in Post.objects.all().order_by('-id'):
        messages_to_display.append(post)

    messages_to_display.sort(key=lambda x: x.processed, reverse=True)
    return render(request, 'announcements/announcements.html', {'tab': 'index', 'posts': messages_to_display, 'nextButtonLink':nextButtonLink, 'previousButtonLink': previousButtonLink})

def contact(request):
	return render(request, 'csss/basic.html', {'content':['If you would like to contact me, please email me', 'csss-webmaster@sfu.ca']})
