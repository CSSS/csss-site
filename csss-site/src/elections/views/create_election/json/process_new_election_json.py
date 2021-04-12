import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants import JSON_INPUT_FIELD_KEY, ELECTION_TYPE_KEY, \
    ELECTION_DATE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY
from elections.views.validators.json.validate_and_return_election_json import validate_and_return_election_json
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_election_date import validate_json_election_date_and_time
from elections.views.validators.validate_nominees_for_new_election import \
    validate_new_nominees_for_new_election
from elections.views.save_election.save_new_election_from_jformat import save_new_election_from_jformat

logger = logging.getLogger('csss_site')


def process_new_inputted_json_election(request, context):
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
    if JSON_INPUT_FIELD_KEY not in request.POST:
        error_message = "Could not find the json in the input"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_election()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_KEY] = None
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_messages, election_json = validate_and_return_election_json(
        request.POST[JSON_INPUT_FIELD_KEY]
    )
    if not success:
        context[ERROR_MESSAGES_KEY] = error_messages
        context[JSON_INPUT_FIELD_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    if not (ELECTION_TYPE_KEY in election_json and ELECTION_DATE_KEY in election_json and
            ELECTION_WEBSURVEY_LINK_KEY in election_json and ELECTION_NOMINEES_KEY in election_json):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_TYPE_KEY}, {ELECTION_DATE_KEY}, {ELECTION_WEBSURVEY_LINK_KEY}, " \
                        f"{ELECTION_NOMINEES_KEY}"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_election()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_type(election_json[ELECTION_TYPE_KEY])
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_json_election_date_and_time(election_json[ELECTION_DATE_KEY])
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_new_nominees_for_new_election(
        election_json[ELECTION_NOMINEES_KEY]
    )
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    election_slug = save_new_election_from_jformat(
        json.loads(request.POST[JSON_INPUT_FIELD_KEY])
    )
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election_slug}/')
