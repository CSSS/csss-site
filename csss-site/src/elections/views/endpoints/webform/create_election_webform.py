import logging

from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.views.create_election.webform.process_new_election_webform import process_new_inputted_webform_election
from elections.views.Constants import TAB_STRING
from elections.views.create_context.webform.create_webform_context import create_webform_context

logger = logging.getLogger('csss_site')


def display_and_process_html_for_new_webform_election(request):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    """
    logger.info(
        "[elections/create_election_json.py display_and_process_html_for_new_json_election()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    context.update(create_webform_context())
    return process_new_inputted_webform_election(request, context) \
        if request.method == "POST" \
        else render(request, 'elections/create_election/create_election_webform.html', context)
