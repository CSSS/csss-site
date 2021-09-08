import json
import logging

from django.shortcuts import render

from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from csss.views.views import ERROR_MESSAGES_KEY
from elections.views.Constants import ELECTION_ID, TAB_STRING, UPDATE_EXISTING_ELECTION__NAME
from elections.views.update_election.json.display_json_for_selected_election_json import \
    display_current_json_election_json
from elections.views.update_election.json.process_existing_election_json import \
    process_existing_election_information_from_json

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_json_election(request):
    """
    Shows the requested election to the user in JSON format
    """
    logger.info(
        "[elections/display_and_process_html_for_json.py "
        "display_and_process_html_for_modification_of_json_election()] request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    html_page = 'elections/update_election/update_election_json.html'
    context = create_context_for_election_officer(request, tab=TAB_STRING, html=html_page)

    if not (ELECTION_ID in request.POST or ELECTION_ID in request.session):
        context[ERROR_MESSAGES_KEY] = ["Unable to locate the Election ID in the request"]
        return render(request, html_page, context)

    process_election = (request.method == "POST") and (UPDATE_EXISTING_ELECTION__NAME in request.POST)

    return process_existing_election_information_from_json(request, context) \
        if process_election else display_current_json_election_json(request, context)
