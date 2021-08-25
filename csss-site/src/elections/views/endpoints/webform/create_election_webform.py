import json
import logging

from django.shortcuts import render

from csss.views.context_creation.create_context_for_election_officer import create_context_for_election_officer
from elections.views.Constants import TAB_STRING
from elections.views.create_election.webform.process_new_election_webform import process_new_inputted_webform_election
from elections.views.create_context.webform.create_webform_context import create_webform_context

logger = logging.getLogger('csss_site')


def display_and_process_html_for_new_webform_election(request):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    """
    logger.info(
        "[elections/create_election_webform.py display_and_process_html_for_new_webform_election()] "
        "request.POST"
    )
    logger.info(json.dumps(request.POST, indent=3))
    html_page = 'elections/create_election/create_election__webform.html'
    context = create_context_for_election_officer(
        request, TAB_STRING, html=html_page
    )

    context.update(create_webform_context())
    process_election = request.method == "POST"

    return process_new_inputted_webform_election(request, context) \
        if process_election \
        else render(request, html_page, context)
