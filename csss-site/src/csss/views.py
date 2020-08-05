import datetime
import logging
import math
from email.utils import parseaddr

from django.shortcuts import render
from django_mailbox.models import Message

from about.models import AnnouncementEmailAddress
from announcements.models import Post
from csss.views_helper import create_main_context, ERROR_MESSAGE_KEY

logger = logging.getLogger('csss_site')


def index(request):
    current_page = request.GET.get('p', 'none')
    if current_page == 'none':
        current_page = 1
    else:
        current_page = int(current_page)

    request_path = request.path

    sfu_emails = [email.email for email in AnnouncementEmailAddress.objects.all()]
    logger.info(f"[csss/views.py index()] sfu_emails {sfu_emails}")

    messages = Message.objects.all().order_by('-id')

    valid_messages = [message for message in messages if message.from_address[0] in sfu_emails]

    sorted_messages = []
    for message in valid_messages:
        # will modify the processed date to be change
        # from the day the mailbox was polled to the date the email was sent
        try:
            dt = datetime.datetime.strptime(message.get_email_object().get('date'), '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            dt = datetime.datetime.strptime(message.get_email_object().get('date')[:-6], '%a, %d %b %Y %H:%M:%S %z')
        message.processed = dt
        message.from_header = parseaddr(message.from_header)[0]
        sorted_messages.append(message)

    for post in Post.objects.all().order_by('-id'):
        sorted_messages.append(post)

    sorted_messages.sort(key=lambda x: x.processed, reverse=True)

    number_of_valid_messages = len(sorted_messages)

    lower_bound = (((current_page - 1) * 5) + 1)
    upper_bound = current_page * 5

    messages_to_display = []
    index = 0
    for media in sorted_messages:
        index += 1
        if (lower_bound <= index) and (index <= upper_bound):
            messages_to_display.append(media)

    if current_page == 1:
        previous_page = math.floor((number_of_valid_messages / 5) + 1)
        next_page = 2
    elif current_page == math.floor((number_of_valid_messages / 5) + 1):
        previous_page = current_page - 1
        next_page = 1
    else:
        previous_page = current_page - 1
        next_page = current_page + 1

    previous_button_link = request_path + '?p=' + str(previous_page)
    next_button_link = request_path + '?p=' + str(next_page)

    context = create_main_context(request, 'index')
    context.update({
        'posts': messages_to_display,
        'nextButtonLink': next_button_link,
        'previousButtonLink': previous_button_link,
    })
    return render(request, 'announcements/announcements.html', context)


def errors(request):
    context = create_main_context(request, 'index')
    if ERROR_MESSAGE_KEY in request.session:
        context['error_experienced'] = request.session[ERROR_MESSAGE_KEY].split("<br>")
        del request.session[ERROR_MESSAGE_KEY]
    return render(request, 'csss/error.html', context)
