import logging

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.views.create_election.display_json_for_new_election_json import display_empty_election_json
from elections.views.create_election.process_new_election_json import process_new_inputted_election
from elections.views.election_management import TAB_STRING
from elections.views.utils.create_election_context import create_context

logger = logging.getLogger('csss_site')


def display_and_process_html_for_new_json_election(request):
    """
    Shows the page where the json is displayed so that the user inputs the data needed to create a new election
    """
    logger.info(
        "[elections/show_page_for_user_input.py display_and_process_html_for_new_json_election()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    context.update(create_context())
    return process_new_inputted_election(request, context) \
        if request.method == "POST" else display_empty_election_json(request, context)
