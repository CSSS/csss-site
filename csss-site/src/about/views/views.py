import datetime
import logging

from django.shortcuts import render

from about.models import Term, Officer
from csss.views_helper import create_main_context

logger = logging.getLogger('csss_site')
TAB_STRING = 'about'


def index(request):
    return render(
        request,
        'about/who_we_are.html',
        create_main_context(request, TAB_STRING)
    )


def list_of_officers(request):
    context = create_main_context(request, TAB_STRING)
    officers = Officer.objects.all().filter().order_by('elected_term__term_number', 'term_position_number')
    now = datetime.datetime.now()
    term_active = (now.year * 10)
    if int(now.month) <= 4:
        term_active += 1
    elif int(now.month) <= 8:
        term_active += 2
    else:
        term_active += 3
    terms = Term.objects.all().order_by('-term_number')
    context.update({
        'officers': officers,
        'term_active': term_active,
        'terms': terms,
    })
    return render(request, 'about/list_of_officers.html', context)
