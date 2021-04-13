import logging

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY
from elections.views.Constants import TAB_STRING
from elections.views.update_election.webform.display_webform_for_selected_election_webform import \
    display_current_webform_election
from elections.views.update_election.webform.process_existing_election_webform import \
    process_existing_election_information_from_webform
from elections.views.create_context.webform.create_webform_context import create_webform_context

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_webform_election(request):
    """Shows the request election to the user in WebForm format"""
    logger.info(f"[administration/display_and_process_html_for_webform.py "
                f"display_and_process_html_for_modification_of_webform_election()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    context.update(create_webform_context())
    return process_existing_election_information_from_webform(request, context) \
        if request.method == "POST" else display_current_webform_election(request, context)
