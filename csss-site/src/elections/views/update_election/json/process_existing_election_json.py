import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from elections.views.Constants import ELECTION_JSON__KEY, ELECTION_ID, \
    SAVE_ELECTION__VALUE, ENDPOINT_MODIFY_VIA_JSON, UPDATE_EXISTING_ELECTION__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.json.create_json_context import \
    create_json_election_context_from_user_inputted_election_dict
from elections.views.extractors.get_existing_election_by_id import get_existing_election_by_id
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat
from elections.views.validators.json.validate_and_return_election_json import validate_and_return_election_json
from elections.views.validators.validate_election_date import validate_json_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_http_link
from elections.views.validators.validate_new_election_json_dict import all_relevant_election_json_keys_exist
from elections.views.validators.validate_nominees_for_existing_election_jformat import \
    validate_nominees_for_existing_election_jformat
from elections.views.validators.validate_user_command import validate_user_command

logger = logging.getLogger('csss_site')


def process_existing_election_information_from_json(request, context):
    """
    Takes in the user's existing election input and validates it before having it saved

    Keyword Argument:
    request -- the django request object that the new election is contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error

     Return
     either redirect user back to the page where they inputted the election info or direct them to the election page
    """
    if not (ELECTION_ID in request.POST and ELECTION_JSON__KEY in request.POST):
        error_message = "Could not find the json in the input"
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)

    if not validate_user_command(request, create_new_election=False):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)

    success, error_message, election_dict = validate_and_return_election_json(
        request.POST[ELECTION_JSON__KEY]
    )
    if not success:
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict, create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)
    if not all_relevant_election_json_keys_exist(election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, {ELECTION_JSON_KEY__DATE}, " \
                        f"{ELECTION_JSON_KEY__WEBSURVEY}, {ELECTION_JSON_KEY__NOMINEES}"
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict, create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)
    election_id = request.POST[ELECTION_ID]
    election = get_existing_election_by_id(election_id)
    if election is None:
        error_message = f"The Selected election for date {election_dict[ELECTION_JSON_KEY__DATE]} " \
                        f"does not exist"
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            election_id=election_id, error_message=error_message, election_information=election_dict,
            create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)
    logger.info(
        f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
        f"election_dict={election_dict}")

    success, error_message = validate_json_election_date_and_time(election_dict[ELECTION_JSON_KEY__DATE])
    if not success:
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            election_id=election_id, error_message=error_message, election_information=election_dict,
            create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)

    success, error_message = validate_election_type(
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            election_id=election_id, error_message=error_message, election_information=election_dict,
            create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            error_message=error_message, election_information=election_dict,
            create_new_election=False
        ))
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_nominees_for_existing_election_jformat(
        election.id, election_dict[ELECTION_JSON_KEY__NOMINEES]
    )
    if not success:
        logger.info(
            f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
            f"{error_message}"
        )
        context.update(create_json_election_context_from_user_inputted_election_dict(
            election_id=election_id, error_message=error_message, election_information=election_dict,
            create_new_election=False
        ))
        return render(request, 'elections/update_election/update_election_json.html', context)
    update_existing_election_obj_from_jformat(
        election,
        election_dict[ELECTION_JSON_KEY__DATE],
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
        election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    )
    save_new_or_update_existing_nominees_jformat(election, election_dict)
    if request.POST[UPDATE_EXISTING_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        if ELECTION_ID in request.session:
            del request.session[ELECTION_ID]
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        request.session[ELECTION_ID] = election.id
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{ENDPOINT_MODIFY_VIA_JSON}')
