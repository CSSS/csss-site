import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.election_management import JSON_INPUT_FIELD_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_DATE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY
from elections.views.extractors.get_election_from_json import save_new_election_from_json
from elections.views.validators.validate_and_return_election_json import validate_and_return_election_json
from elections.views.validators.validate_election_date import validate_election_date
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_nominees_for_new_election_json import \
    validate_new_nominees_for_new_election_from_json

logger = logging.getLogger('csss_site')


def process_new_inputted_election(request, context):
    """
    Takes in the user's new election input and validates it before having it saved

    Keyword Argument:
    request -- the django request object that the new election is contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error

     Return
     either redirect user back to the page where they inputted the election info or direct them to the newly created
      election page
    """
    if JSON_INPUT_FIELD_POST_KEY not in request.POST:
        error_message = "Could not find the json in the input"
        logger.info("[elections/validate_election_type.py validate_inputted_election_json()] "
                    f"{error_message}")
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_POST_KEY] = None
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_messages, election_json = validate_and_return_election_json(
        request.POST[JSON_INPUT_FIELD_POST_KEY]
    )
    if not success:
        context[ERROR_MESSAGES_KEY] = error_messages
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    if not (ELECTION_TYPE_POST_KEY in election_json and ELECTION_DATE_POST_KEY in election_json and
            ELECTION_WEBSURVEY_LINK_POST_KEY in election_json and ELECTION_NOMINEES_POST_KEY in election_json):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_TYPE_POST_KEY}, {ELECTION_DATE_POST_KEY}, {ELECTION_WEBSURVEY_LINK_POST_KEY}, " \
                        f"{ELECTION_NOMINEES_POST_KEY}"
        logger.info(
            f"[elections/validate_election_type.py validate_inputted_election_json()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_type(election_json[ELECTION_TYPE_POST_KEY])
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_date(election_json[ELECTION_DATE_POST_KEY])
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_new_nominees_for_new_election_from_json(
        election_json[ELECTION_NOMINEES_POST_KEY]
    )
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    election_slug = save_new_election_from_json(
        json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY])
    )
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election_slug}/')
