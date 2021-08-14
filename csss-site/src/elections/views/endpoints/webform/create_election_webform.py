import json
import logging

from django.shortcuts import render

from administration.views.verify_user_access import create_context_and_verify_user_can_manage_elections
from csss.views_helper import ERROR_MESSAGE_KEY
from elections.views.Constants import TAB_STRING
from elections.views.create_context.webform.create_webform_context import create_webform_context
from elections.views.create_election.webform.process_new_election_webform import process_new_inputted_webform_election

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
    (render_value, error_message, context) = create_context_and_verify_user_can_manage_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    context.update(create_webform_context())
    process_election = request.method == "POST"

    return process_new_inputted_webform_election(request, context) \
        if process_election \
        else render(request, 'elections/create_election/create_election__webform.html', context)
