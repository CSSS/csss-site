import json

from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.views.Constants import TAB_STRING


def election_officer_documentation(request):
    logger = Loggers.get_logger()
    logger.info(
        "[elections/election_officer_documentation.py election_officer_documentation()] "
        "request.POST"
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_election_officer(request, tab=TAB_STRING)
    return render(request, 'elections/election_officer_documentation.html', context)
