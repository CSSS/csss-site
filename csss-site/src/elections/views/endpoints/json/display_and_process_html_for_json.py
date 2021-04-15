import logging

from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY, \
    ERROR_MESSAGES_KEY
from elections.views.create_context.json.create_json_context import create_json_context
from elections.views.Constants import TAB_STRING, DISPLAY_ELECTION_KEY
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
        "display_and_process_html_for_modification_of_json_election()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(
        request, TAB_STRING
    )
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if request.method != "POST":
        context[ERROR_MESSAGES_KEY] = ["Unable to locate the Election ID in the request"]
        return render(request, 'elections/update_election/update_election_json.html', context)

    context.update(create_json_context())
    return display_current_json_election_json(request, context)  \
        if DISPLAY_ELECTION_KEY in request.POST else process_existing_election_information_from_json(request, context)
