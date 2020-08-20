import logging

from django.shortcuts import render

from announcements.models import Announcement, LatestAnnouncementPage
from csss.views_helper import create_main_context, ERROR_MESSAGE_KEY

logger = logging.getLogger('csss_site')


def index(request):
    current_page = request.GET.get('p', 'none')
    if current_page == 'none':
        current_page = 1
    else:
        current_page = int(current_page)

    request_path = request.path

    latest_page_number = LatestAnnouncementPage.objects.get()

    announcements = Announcement.objects.all().filter(page_number=latest_page_number.page_number).order_by('-id')
    messages_to_display = []
    for announcement in announcements:
        if announcement.post is None:
            messages_to_display.extend(announcement.email)
        else:
            messages_to_display.extend(announcement.post)

    messages_to_display.sort(key=lambda x: x.processed, reverse=True)

    if current_page is latest_page_number:
        previous_page = latest_page_number-1
        next_page = 0
    elif current_page == 0:
        previous_page = latest_page_number
        next_page = 1
    else:
        previous_page = current_page-1
        next_page = current_page+1

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
