import logging

from django.core.paginator import Paginator
from django.shortcuts import render

from announcements.models import PostsAndEmails, Post
from csss.views_helper import create_main_context, ERROR_MESSAGE_KEY

logger = logging.getLogger('csss_site')


def index(request):
    current_page = request.GET.get('p', 'none')
    if current_page == 'none':
        current_page = 1
    else:
        current_page = int(current_page)

    request_path = request.path

    paginated_object = Paginator(PostsAndEmails.objects.all().filter(show=True), per_page=5)
    paginated_object = Paginator(Post.objects.all().order_by('id'), per_page=5)

    previous_button_link = request_path + '?p=' + str(
        current_page - 1 if current_page >= 0 else paginated_object.num_pages)
    next_button_link = request_path + '?p=' + str(
        current_page + 1 if current_page + 1 <= paginated_object.num_pages else 0)

    context = create_main_context(request, 'index')
    context.update({
        'posts': paginated_object.page(current_page),
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
