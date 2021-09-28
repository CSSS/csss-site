import json
import logging

from django.shortcuts import render

from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import TAB_STRING, UPDATE_EXISTING_ELECTION__NAME
from elections.views.create_context.webform.create_webform_context import create_webform_context
from elections.views.update_election.webform.display_webform_for_selected_election_webform import \
    display_current_webform_election
from elections.views.update_election.webform.process_existing_election_webform import \
    process_existing_election_information_from_webform

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_webform_election(request, slug):
    """Shows the request election to the user in WebForm format"""
    logger.info("[elections/display_and_process_html_for_webform.py "
                "display_and_process_html_for_modification_of_webform_election()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))

    context = create_context_for_election_officer(request, tab=TAB_STRING)

    if len(Election.objects.all().filter(slug=slug)) != 1:
        context[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return render(request, 'elections/update_election/update_election__webform.html', context)

    process_election = (request.method == "POST") and (UPDATE_EXISTING_ELECTION__NAME in request.POST)
    context.update(create_webform_context(create_new_election=False))

    election = Election.objects.get(slug=slug)
    return process_existing_election_information_from_webform(request, election, context) \
        if process_election else \
        display_current_webform_election(request, election, context)
