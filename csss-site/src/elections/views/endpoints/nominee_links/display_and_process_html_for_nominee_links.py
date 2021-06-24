import json
import logging

from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY, \
    ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import TAB_STRING, UPDATE_EXISTING_ELECTION__NAME
from elections.views.update_election.nominee_links.display_selected_election_nominee_links import \
    display_selected_election_and_nominee_links
from elections.views.update_election.nominee_links.process_existing_election_and_nominee_links import \
    process_existing_election_and_nominee_links

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_election_and_nominee_links__nominee_links(request, slug):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    """
    logger.info(
        "[elections/display_and_process_html_for_nominee_links.py "
        "display_and_process_html_for_modification_of_election_and_nominee_links__nominee_links()] "
        "request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    if len(Election.objects.all().filter(slug=slug)) != 1:
        context[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)

    process_election = (request.method == "POST") and (UPDATE_EXISTING_ELECTION__NAME in request.POST)

    return process_existing_election_and_nominee_links(request, context, slug) if process_election \
        else display_selected_election_and_nominee_links(request, context, slug)
