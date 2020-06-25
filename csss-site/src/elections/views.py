import logging
from datetime import datetime

from django.shortcuts import render

# Create your views here.
# from django.views import generic
from administration.views.views_helper import create_context
from .models import NominationPage, Nominee

logger = logging.getLogger('csss_site')
TAB_STRING = 'elections'


def get_nominees(request, slug):
    context = create_context(request, TAB_STRING)
    retrieved_obj = NominationPage.objects.filter(slug=slug)
    if retrieved_obj[0].date <= datetime.now():
        logger.info("[elections/login_views.py get_nominees()] time to vote")
        nominees = Nominee.objects.filter(nomination_page__slug=slug).all().order_by('position')
        context.update({
            'election': retrieved_obj[0],
            'election_date': retrieved_obj[0].date.strftime("%Y-%m-%d"),
            'nominees': nominees,
        })
        return render(request, 'elections/nominee_list.html', context)
    else:
        logger.info("[elections/login_views.py get_nominees()] cant vote yet")
        context.update({
            'nominees': 'none',
        })
        return render(request, 'elections/nominee_list.html', context)
