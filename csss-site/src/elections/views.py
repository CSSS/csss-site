from django.shortcuts import render

# Create your views here.
# from django.views import generic
from csss.views_helper import create_context
from .models import NominationPage, Nominee
from datetime import datetime
from django.conf import settings

import logging
logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    retrieved_obj = NominationPage.objects.filter(slug=slug)
    context = create_context(request, 'elections')
    if retrieved_obj[0].date <= datetime.now():
        logger.info("[elections/views.py get_nominees()] time to vote")
        context.update({
            'election': retrieved_obj[0],
            'election_date': retrieved_obj[0].date.strftime("%Y-%m-%d"),
            'nominees': Nominee.objects.filter(nomination_page__slug=slug).all().order_by('position'),
        })
        return render(request, 'elections/nominee_list.html', context)
    else:
        logger.info("[elections/views.py get_nominees()] cant vote yet")
        context.update({'nominees': 'none'})
        return render(request, 'elections/nominee_list.html', context)
