import json

from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import TAB_STRING, UPDATE_EXISTING_ELECTION__NAME
from elections.views.update_election.json.display_json_for_selected_election_json import \
    display_current_json_election_json
from elections.views.update_election.json.process_existing_election_json import \
    process_existing_election_information_from_json

logger = get_logger()


def display_and_process_html_for_modification_of_json_election(request, slug):
    """
    Shows the requested election to the user in JSON format
    """
    logger.info(
        "[elections/display_and_process_html_for_json.py "
        "display_and_process_html_for_modification_of_json_election()] request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_election_officer(request, tab=TAB_STRING)

    if len(Election.objects.all().filter(slug=slug)) != 1:
        context[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return render(request, 'elections/update_election/update_election_json.html', context)

    process_election = (request.method == "POST") and (UPDATE_EXISTING_ELECTION__NAME in request.POST)
    election = Election.objects.get(slug=slug)
    return process_existing_election_information_from_json(request, election, context) \
        if process_election else display_current_json_election_json(request, election, context)
