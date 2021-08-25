import logging

from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context
from elections.views.Constants import TAB_STRING

logger = logging.getLogger('csss_site')


def list_of_elections(request):
    logger.info("[elections/list_of_elections.py list_of_elections()]")
    return render(request, 'elections/list_elections.html', create_main_context(request, TAB_STRING))
