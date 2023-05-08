import json

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views_helper import verify_user_input_has_all_required_fields
from elections.views.Constants import ELECTION_JSON__KEY, CREATE_NEW_ELECTION__NAME, \
    SAVE_ELECTION__VALUE, ENDPOINT_MODIFY_VIA_JSON
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__END_DATE
from elections.views.save_election.save_new_election_from_jformat import save_new_election_from_jformat
from elections.views.update_election.json.process_existing_election_json import \
    create_json_election_context_from_user_inputted_election_dict
from elections.views.validators.json.validate_and_return_election_json import validate_and_return_election_json
from elections.views.validators.validate_election_date import validate_json_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_election_uniqueness import validate_election_json_uniqueness
from elections.views.validators.validate_link import validate_websurvey_link
from elections.views.validators.validate_new_election_json_dict import all_relevant_election_json_keys_exist
from elections.views.validators.validate_nominees_for_new_election import \
    validate_new_nominees_for_new_election
from elections.views.validators.validate_user_command import validate_user_command


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
    logger = Loggers.get_logger()
    fields = [ELECTION_JSON__KEY]
    error_message = verify_user_input_has_all_required_fields(request.POST, fields=fields)
    if error_message != "":
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(error_message=error_message))
        return render(request, 'elections/create_election/create_election_json.html', context)

    if not validate_user_command(request):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(error_message=error_message))
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message, election_dict = validate_and_return_election_json(
        request.POST[ELECTION_JSON__KEY]
    )
    if not success:
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)

    if not all_relevant_election_json_keys_exist(election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, {ELECTION_JSON_KEY__DATE}, " \
                        f"{ELECTION_JSON_KEY__END_DATE}, " \
                        f"{ELECTION_JSON_KEY__WEBSURVEY}, {ELECTION_JSON_KEY__NOMINEES}"
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_type(
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_websurvey_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY])
    if not success:
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)
    success, error_message = validate_json_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE])
    if not success:
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)\

    success, error_message = validate_election_json_uniqueness(election_dict)
    if not success:
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_new_nominees_for_new_election(
        election_dict[ELECTION_JSON_KEY__NOMINEES]
    )
    if not success:
        logger.info(
            f"[elections/process_new_election_json.py process_new_inputted_json_election()] {error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict)
        )
        return render(request, 'elections/create_election/create_election_json.html', context)

    election = save_new_election_from_jformat(
        json.loads(request.POST[ELECTION_JSON__KEY])
    )
    if request.POST[CREATE_NEW_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_JSON}')
