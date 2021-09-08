import logging
import os

import markdown
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render

from announcements.models import Announcement
from csss.views.context_creation.create_main_context import create_main_context
from csss.views_helper import ERROR_MESSAGE_KEY

logger = logging.getLogger('csss_site')

ERROR_MESSAGES_KEY = 'error_messages'


def check_if_file_attachments_exists(message):
    """
    Checks all the attachments for the message and returns true if any of them don't exist

    Keyword Argument
    message -- the message whose attachments have to be checked

    Return
    bool -- True if any of the attachments don't exist, False otherwise
    """
    if message.email is not None:
        for attachment in message.email.attachments.all():
            if not os.path.exists(attachment.document.path):
                return True
    return False


def index(request):
    current_page = request.GET.get('p', 'none')
    if current_page == 'none':
        current_page = 1
    else:
        current_page = int(current_page)

    request_path = request.path

    paginated_object = Paginator(Announcement.objects.all().filter(display=True).order_by('-date'), per_page=5)

    if paginated_object.num_pages < current_page:
        return HttpResponseRedirect(f'{settings.URL_ROOT}')

    announcements = paginated_object.page(current_page)
    error_message = None
    if settings.ENVIRONMENT == "LOCALHOST":
        announcement = [announcement for announcement in announcements if
                        check_if_file_attachments_exists(announcement)]
        if len(announcement) > 0:
            error_message = (
                "run <br>`python3 manage.py create_attachments`<br> or "
                "<br>`python3 manage.py create_attachments --download`"
            )

    previous_button_link = request_path + '?p=' + str(
        current_page - 1 if current_page > 1 else paginated_object.num_pages
    )
    next_button_link = request_path + '?p=' + str(
        current_page + 1 if current_page + 1 <= paginated_object.num_pages else 1
    )
    context = create_main_context(request, 'index')
    context.update({
        'announcements': announcements,
        'error_message': error_message,
        'nextButtonLink': next_button_link,
        'previousButtonLink': previous_button_link,
        'URL_ROOT_FOR_EMAIL_ATTACHMENTS': settings.URL_ROOT[:-1],
        'URL_ROOT': settings.URL_ROOT,
        'ENVIRONMENT': settings.ENVIRONMENT
    })
    return render(request, 'announcements/announcements.html', context)


def md(request):
    context = create_main_context(request, 'index')
    if 'message' in request.POST:
        context['md'] = markdown.markdown(
            request.POST['message'], extensions=[
                'sane_lists', 'markdown_link_attr_modifier'
            ],
            extension_configs={
                'markdown_link_attr_modifier': {
                    'new_tab': 'on',
                },
            }
        )
        context['message'] = request.POST['message']

    return render(request, 'csss/markdown_preview.html', context)
