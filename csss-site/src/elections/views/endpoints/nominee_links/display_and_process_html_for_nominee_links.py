import json

from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election, NomineeLink
from elections.views.Constants import TAB_STRING
from elections.views.create_context.nominee_links.create_or_update_election.\
    create_context_for_update_election_nominee_links_html import \
    create_context_for_update_election_nominee_links_html
from elections.views.update_election.nominee_links.process_existing_election_and_nominee_links import \
    process_existing_election_and_nominee_links


def display_and_process_html_for_modification_of_election_and_nominee_links__nominee_links(request, slug):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    """
    logger = Loggers.get_logger()
    logger.info(
        "[elections/display_and_process_html_for_nominee_links.py "
        "display_and_process_html_for_modification_of_election_and_nominee_links__nominee_links()] "
        "request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_election_officer(request, tab=TAB_STRING)

    if len(Election.objects.all().filter(slug=slug)) != 1:
        context[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )

    process_election = (request.method == "POST")
    election = Election.objects.get(slug=slug)

    if process_election:
        return process_existing_election_and_nominee_links(request, election, context)
    else:
        create_context_for_update_election_nominee_links_html(
            context, nominee_links=NomineeLink.objects.all().order_by('id'),
            election_date=election.date, election_time=election.date, election_end_date=election.end_date,
            election_type=election.election_type, websurvey_link=election.websurvey,
            create_new_election=election is None, election_obj=election
        )
        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )
