import logging

from django.shortcuts import render

from csss.views_helper import create_main_context
from elections.views.Constants import TAB_STRING

logger = logging.getLogger('csss_site')


def list_of_elections(request):
    logger.info("[elections/list_of_elections.py list_of_elections()]")
    context = create_main_context(request, TAB_STRING)
    return render(request, 'elections/list_elections.html', context)
