import json
import logging

from csss.views_helper import create_context_for_election_officer
from elections.views.Constants import TAB_STRING, CREATE_NEW_ELECTION__NAME
from elections.views.create_election.json.display_json_for_new_election import display_empty_election_json
from elections.views.create_election.json.process_new_election_json import process_new_inputted_json_election

logger = logging.getLogger('csss_site')


def display_and_process_html_for_new_json_election(request):
    """
    Shows the page where the json is displayed so that the user inputs the data needed to create a new election
    """
    logger.info(
        "[elections/create_election_json.py display_and_process_html_for_new_json_election()] request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_election_officer(
        request, TAB_STRING, html='elections/create_election/create_election_json.html'
    )
    process_election = request.method == "POST" and CREATE_NEW_ELECTION__NAME in request.POST

    return process_new_inputted_json_election(request, context) \
        if process_election else display_empty_election_json(request, context)
