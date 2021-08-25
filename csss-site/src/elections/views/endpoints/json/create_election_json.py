import json
import logging

from csss.views.request_validation import verify_access_logged_user_and_create_context_for_elections
from csss.views_helper import ERROR_MESSAGE_KEY
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
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    process_election = request.method == "POST" and CREATE_NEW_ELECTION__NAME in request.POST

    return process_new_inputted_json_election(request, context) \
        if process_election else display_empty_election_json(request, context)
