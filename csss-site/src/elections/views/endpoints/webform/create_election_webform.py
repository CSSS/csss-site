import json

from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.views.Constants import TAB_STRING
from elections.views.create_context.webform.create_context_for_create_election__webform_html import \
    create_context_for_create_election__webform_html
from elections.views.create_election.webform.process_new_election_webform import process_new_inputted_webform_election


def display_and_process_html_for_new_webform_election(request):
    """
    Shows the page where the webform is displayed so that the user inputs the data needed to create a new election
    """
    logger = Loggers.get_logger()
    logger.info(
        "[elections/create_election_webform.py display_and_process_html_for_new_webform_election()] "
        "request.POST"
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_election_officer(request, tab=TAB_STRING)

    if request.method == "POST":
        return process_new_inputted_webform_election(request, context)
    else:
        create_context_for_create_election__webform_html(context)
        return render(request, 'elections/webform/create_election__webform.html', context)
