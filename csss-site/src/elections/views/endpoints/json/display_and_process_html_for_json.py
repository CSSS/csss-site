import logging

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.views.create_context.json.create_json_context import create_json_context
from elections.views.Constants import TAB_STRING
from elections.views.update_election.json.display_json_for_selected_election_json import display_current_json_election_json
from elections.views.update_election.json.process_existing_election_json import \
    process_existing_election_information_from_json

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_json_election(request):
    """
    Shows the requested election to the user in JSON format
    """
    logger.info(
        "[elections/display_and_process_html_for_webform.py "
        "display_and_process_html_for_modification_of_json_election()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    context.update(create_json_context())
    return process_existing_election_information_from_json(request, context) \
        if request.method == "POST" else display_current_json_election_json(request, context)
