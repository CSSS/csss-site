import json

from django.shortcuts import render

from csss.setup_logger import Loggers
from elections.views.Constants import TAB_STRING
from elections.views.create_context.create_context_for_websurvey_results_import import \
    create_context_for_websurvey_results_import


def import_websurvey_results(request):
    logger = Loggers.get_logger()
    context = create_context_for_websurvey_results_import(request, tab=TAB_STRING)
    logger.info("[elections/import_websurvey_results.py import_websurvey_results()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    return render(request, 'elections/import_websurvey_results.html', context)
