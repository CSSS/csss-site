import json
import logging

from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context
from csss.views.request_validation import validate_request_to_manage_elections
from elections.views.Constants import TAB_STRING
from elections.views.create_context.nominee_links.create_election_nominee_links_html import \
    create_context_for_create_election_nominee_links_html
from elections.views.create_election.nominee_links.process_new_election_and_nominee_links import \
    process_new_election_and_nominee_links

logger = logging.getLogger('csss_site')


def display_and_process_html_for_new_nominee_links_election(request):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    via Nominee Links
    """
    logger.info(
        "[elections/create_election_nominee_links.py display_and_process_html_for_new_nominee_links_election()] "
        "request.POST"
    )
    logger.info(json.dumps(request.POST, indent=3))
    html_page = 'elections/create_election/create_election_nominee_links.html'
    validate_request_to_manage_elections(request, html=html_page)
    context = create_main_context(request, TAB_STRING)

    if request.method == "POST":
        return process_new_election_and_nominee_links(request, context)
    else:
        create_context_for_create_election_nominee_links_html(context, create_new_election=True)
        return render(request, html_page, context)
