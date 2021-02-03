import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from elections.views.create_new_election_with_json.extraction.extract_from_json import \
    validate_new_election
from elections.views.create_new_election_with_json.validation.validate_json import validate_inputted_election_json
from elections.views.election_management import TAB_STRING, JSON_INPUT_FIELD_POST_KEY

logger = logging.getLogger('csss_site')


def process_new_election_information_from_json(request):
    """
    Processes the user's input from the JSON page for creating a new election
    """
    logger.info(
        f"[elections/election_management.py process_new_election_information_from_json()] request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    logger.info(
        "[elections/election_management.py process_new_election_information_from_json()] creating new election"
    )
    success, error_messages, election_json = validate_inputted_election_json(request)
    if not success:
        context[ERROR_MESSAGES_KEY] = error_messages
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election_json.html', context)

    election_slug = validate_new_election(request)
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election_slug}/')
