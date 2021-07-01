import json
import logging

from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY
from elections.models import NomineeLink
from elections.views.Constants import TAB_STRING, NOMINEE_LINK_ID, \
    CREATE_OR_UPDATE_NOMINEE__NAME
from elections.views.create_context.nominee_links.create_nominee_links_context import \
    create_context_for_update_nominee_html
from elections.views.update_election.nominee_links.display_selected_nominee_nominee_links import \
    display_current_nominee_link_election
from elections.views.update_election.nominee_links.process_nominee__nominee_links import \
    process_nominee__nominee_links

logger = logging.getLogger('csss_site')


def display_and_process_html_for_nominee_modification(request):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    """
    logger.info(
        "[elections/display_and_process_html_for_nominee_modification__nominee_link.py"
        " display_and_process_html_for_nominee_modification()] "
        "request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    nominee_link_id = request.GET.get(NOMINEE_LINK_ID, None)
    nominee_links = NomineeLink.objects.all().filter(id=nominee_link_id)
    error_message = None
    if nominee_link_id is None:
        error_message = ["Unable to locate the Nominee Link ID in the request"]
    if error_message is None and len(nominee_links) != 1:
        error_message = [f"invalid Nominee Link ID of {nominee_link_id} detected in the request"]
    if error_message is None and nominee_links[0].election is None:
        error_message = [f"No election attached to Nominee Link {nominee_links[0]} detected in the request"]
    if error_message is not None:
        context.update(
            create_context_for_update_nominee_html(
                error_messages=error_message
            )
        )
        return render(request, 'elections/update_nominee/update_nominee.html', context)

    process_election = (request.method == "POST") and (CREATE_OR_UPDATE_NOMINEE__NAME in request.POST)

    return process_nominee__nominee_links(request, context, nominee_link_id) if process_election \
        else display_current_nominee_link_election(request, context, nominee_link_id)