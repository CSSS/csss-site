import json
import logging

from django.shortcuts import render

from administration.views.verify_user_access import create_context_and_verify_user_can_manage_elections
from csss.views_helper import ERROR_MESSAGE_KEY, \
    ERROR_MESSAGES_KEY
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
    (render_value, error_message, context) = create_context_and_verify_user_can_manage_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    if not (ELECTION_ID in request.POST or ELECTION_ID in request.session):
        context[ERROR_MESSAGES_KEY] = ["Unable to locate the Election ID in the request"]
        return render(request, 'elections/update_election/update_election_json.html', context)

    process_election = (request.method == "POST") and (UPDATE_EXISTING_ELECTION__NAME in request.POST)

    return process_existing_election_information_from_json(request, context) \
        if process_election else display_current_json_election_json(request, context)
