import json
import logging

from django.shortcuts import render

from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import TAB_STRING
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
    context = create_context_for_election_officer(request, tab=TAB_STRING)

    if len(Election.objects.all().filter(slug=slug)) != 1:
        context[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)

    process_election = (request.method == "POST")
    election = Election.objects.get(slug=slug)

    return process_existing_election_and_nominee_links(request, election, context) if process_election \
        else display_selected_election_and_nominee_links(request, election, context)
