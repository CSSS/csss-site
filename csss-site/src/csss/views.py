import logging

from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
import markdown

from announcements.models import Announcement
from csss.views_helper import create_main_context, ERROR_MESSAGE_KEY

logger = logging.getLogger('csss_site')


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

    previous_button_link = request_path + '?p=' + str(
        current_page - 1 if current_page > 1 else paginated_object.num_pages
    )
    next_button_link = request_path + '?p=' + str(
        current_page + 1 if current_page + 1 <= paginated_object.num_pages else 1
    )

    context = create_main_context(request, 'index')
    context.update({
        'announcements': announcements,
        'nextButtonLink': next_button_link,
        'previousButtonLink': previous_button_link,
        'URL_ROOT_FOR_EMAIL_ATTACHMENTS': settings.URL_ROOT[:-1],
        'URL_ROOT': settings.URL_ROOT,
        'ENVIRONMENT': settings.ENVIRONMENT
    })
    return render(request, 'announcements/announcements.html', context)


def errors(request):
    context = create_main_context(request, 'index')
    if ERROR_MESSAGE_KEY in request.session:
        context['error_experienced'] = request.session[ERROR_MESSAGE_KEY].split("<br>")
        del request.session[ERROR_MESSAGE_KEY]
    return render(request, 'csss/error.html', context)


def md(request):
    context = create_main_context(request, 'index')
    if 'message' in request.POST:
        context['md'] = markdown.markdown(
            request.POST['message'], extensions=['sane_lists', 'markdown_link_attr_modifier'],
            extension_configs={
                'markdown_link_attr_modifier': {
                    'new_tab': 'on',
                },
            }
        )

    return render(request, 'csss/markdown_preview.html', context)
