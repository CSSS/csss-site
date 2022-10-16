import json

from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.views.Constants import TAB_STRING
from elections.views.create_context.nominee_links.create_or_update_election. \
    create_context_for_create_election_nominee_links_html import \
    create_context_for_create_election_nominee_links_html
from elections.views.create_election.nominee_links.process_new_election_and_nominee_links import \
    process_new_election_and_nominee_links

logger = get_logger()


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
    context = create_context_for_election_officer(request, tab=TAB_STRING)

    if request.method == "POST":
        return process_new_election_and_nominee_links(request, context)
    else:
        create_context_for_create_election_nominee_links_html(context, create_new_election=True)
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )
