import json
import logging

from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants_v2 import ELECTION_JSON__KEY, CREATE_NEW_JSON_ELECTION__NAME, \
    SAVE_NEW_JSON_ELECTION__VALUE, SAVE_AND_CONTINUE_EDITING_NEW_JSON_ELECTION__VALUE, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES
from elections.views.endpoints.election_page import get_nominees
from elections.views.save_election.save_new_election_from_jformat import save_new_election_from_jformat
from elections.views.update_election.json.display_json_for_selected_election_json import \
    display_current_json_election_json
from elections.views.validators.json.validate_and_return_election_json import validate_and_return_election_json
from elections.views.validators.validate_election_date import validate_json_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_nominees_for_new_election import \
    validate_new_nominees_for_new_election

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
    if ELECTION_JSON__KEY not in request.POST:
        error_message = "Could not find the json in the input"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_election()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = None
        return render(request, 'elections/create_election/create_election_json.html', context)

    if not valid_user_command(request):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_election()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = None
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message, election_dict = validate_and_return_election_json(
        request.POST[ELECTION_JSON__KEY]
    )
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = json.dumps(election_dict)
        return render(request, 'elections/create_election/create_election_json.html', context)

    if not all_relevant_election_keys_exist(election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, {ELECTION_JSON_KEY__DATE}, " \
                        f"{ELECTION_JSON_KEY__WEBSURVEY}, {ELECTION_JSON_KEY__NOMINEES}"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_election()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = json.dumps(election_dict)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_type(
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = json.dumps(election_dict)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_json_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE])
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = json.dumps(election_dict)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_new_nominees_for_new_election(
        election_dict[ELECTION_JSON_KEY__NOMINEES]
    )
    if not success:
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[ELECTION_JSON__KEY] = json.dumps(election_dict)
        return render(request, 'elections/create_election/create_election_json.html', context)

    election_slug = save_new_election_from_jformat(
        json.loads(request.POST[ELECTION_JSON__KEY])
    )
    if request.POST[CREATE_NEW_JSON_ELECTION__NAME] == SAVE_NEW_JSON_ELECTION__VALUE:
        return get_nominees(request, election_slug)
    else:
        return display_current_json_election_json(request, context)


def valid_user_command(request):
    return (
            CREATE_NEW_JSON_ELECTION__NAME in request.POST and
            request.POST[CREATE_NEW_JSON_ELECTION__NAME] in [
                SAVE_NEW_JSON_ELECTION__VALUE, SAVE_AND_CONTINUE_EDITING_NEW_JSON_ELECTION__VALUE
            ]
    )


def all_relevant_election_keys_exist(election_dict):
    return (
            ELECTION_JSON_KEY__ELECTION_TYPE in election_dict and ELECTION_JSON_KEY__DATE in election_dict and
            ELECTION_JSON_KEY__WEBSURVEY in election_dict and ELECTION_JSON_KEY__NOMINEES in election_dict
    )
