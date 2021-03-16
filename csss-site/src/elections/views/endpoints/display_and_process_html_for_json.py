import logging

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.views.election_management import TAB_STRING
from elections.views.update_election.display_json_for_selected_election_json import display_current_election
from elections.views.update_election.process_existing_election_json import \
    process_existing_election_information_from_json

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_json_election(request):
    """
    Shows the requested election to the user in JSON format
    """
    logger.info(
        f"[administration/election_management.py show_page_for_user_to_modify_election_information_from_json()] "
        f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    return process_existing_election_information_from_json(request, context) \
        if request.method == "POST" else display_current_election(request, context)
