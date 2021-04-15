import json
import logging

from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants import JSON_INPUT_FIELD_KEY, \
    ELECTION_ID_KEY, ELECTION_DATE_KEY, \
    ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, REDIRECT_TO_ELECTION, SUBMIT, \
    SUBMIT_AND_CONTINUE_EDITING, REDIRECT_TO_ELECTION_KEY, SUBMIT_KEY, SUBMIT_AND_CONTINUE_EDITING_KEY
from elections.views.endpoints.election_page import get_nominees
from elections.views.extractors.get_existing_election_by_id import get_existing_election_by_id
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat
from elections.views.update_election.json.display_json_for_selected_election_json import \
    display_current_json_election_json
from elections.views.utils.prepare_json_for_html import prepare_json_for_html
from elections.views.validators.json.validate_and_return_election_json import validate_and_return_election_json
from elections.views.validators.validate_election_date import validate_json_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_nominees_for_existing_election_jformat import \
    validate_nominees_for_existing_election_jformat

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
    if JSON_INPUT_FIELD_KEY not in request.POST or ELECTION_ID_KEY not in request.POST or \
            REDIRECT_TO_ELECTION not in request.POST:
        error_message = "Not all necessary fields were detected in your input"
        context.update(create_json_context(context, None, None, error_message))
        return render(request, 'elections/update_election/update_election_json.html', context)
    logger.info(
        "[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
        "creating new election"
    )
    election_id = request.POST[ELECTION_ID_KEY]
    success, error_message, updated_elections_information = validate_and_return_election_json(
        request.POST[JSON_INPUT_FIELD_KEY]
    )
    if not success:
        context.update(
            create_json_context(context, election_id, prepare_json_for_html(request.POST[JSON_INPUT_FIELD_KEY]),
                                error_message)
        )
        return render(request, 'elections/update_election/update_election_json.html', context)

    election = get_existing_election_by_id(election_id)
    if election is None:
        error_message = f"The Selected election for date {updated_elections_information[ELECTION_DATE_KEY]} " \
                        f"does not exist"
        context.update(create_json_context(context, election_id, updated_elections_information, error_message))
        return render(request, 'elections/update_election/update_election_json.html', context)
    logger.info(
        f"[elections/process_existing_election_json.py process_existing_election_information_from_json()] "
        f"updated_elections_information={updated_elections_information}")
    if not (ELECTION_DATE_KEY in updated_elections_information and
            ELECTION_TYPE_KEY in updated_elections_information and
            ELECTION_WEBSURVEY_LINK_KEY in updated_elections_information and
            ELECTION_NOMINEES_KEY in updated_elections_information):
        error_message = f"Did not find all of the following necessary keys in input: {ELECTION_TYPE_KEY}, " \
                        f"{ELECTION_DATE_KEY}, {ELECTION_WEBSURVEY_LINK_KEY}, {ELECTION_NOMINEES_KEY}"
        context.update(create_json_context(context, election_id, updated_elections_information, error_message))
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_json_election_date_and_time(updated_elections_information[ELECTION_DATE_KEY])
    if not success:
        context.update(create_json_context(context, election_id, updated_elections_information, error_message))
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_election_type(updated_elections_information[ELECTION_TYPE_KEY])
    if not success:
        context.update(create_json_context(context, election_id, updated_elections_information, error_message))
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_nominees_for_existing_election_jformat(
        election.id, updated_elections_information[ELECTION_NOMINEES_KEY]
    )
    if not success:
        context.update(create_json_context(context, election_id, updated_elections_information, error_message))
        return render(request, 'elections/update_election/update_election_json.html', context)
    if request.POST[REDIRECT_TO_ELECTION] not in [SUBMIT, SUBMIT_AND_CONTINUE_EDITING]:
        context.update(
            create_json_context(
                context, election_id, updated_elections_information, "Unable to understand user command"
            )
        )
        return render(request, 'elections/update_election/update_election_json.html', context)
    update_existing_election_obj_from_jformat(
        election,
        updated_elections_information[ELECTION_DATE_KEY],
        updated_elections_information[ELECTION_TYPE_KEY],
        updated_elections_information[ELECTION_WEBSURVEY_LINK_KEY]
    )
    save_new_or_update_existing_nominees_jformat(election, updated_elections_information)
    if request.POST[REDIRECT_TO_ELECTION] == SUBMIT:
        return get_nominees(request, election.slug)
    elif request.POST[REDIRECT_TO_ELECTION] == SUBMIT_AND_CONTINUE_EDITING:
        return display_current_json_election_json(request, context)


def create_json_context(context, election_id=None, election_information=None, error_message=None):
    context.update({
        REDIRECT_TO_ELECTION_KEY: REDIRECT_TO_ELECTION,
        SUBMIT_KEY: SUBMIT,
        SUBMIT_AND_CONTINUE_EDITING_KEY: SUBMIT_AND_CONTINUE_EDITING
    })
    if election_id is not None:
        context[ELECTION_ID_KEY] = election_id
    if election_information is not None:
        context[JSON_INPUT_FIELD_KEY] = json.dumps(election_information)
    if error_message is not None:
        context[ERROR_MESSAGES_KEY] = [error_message]
    return context
