import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.election_management import JSON_INPUT_FIELD_POST_KEY, \
    ELECTION_ID_POST_KEY, ELECTION_DATE_POST_KEY, \
    ELECTION_TYPE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY
from elections.views.election_management_helper import _get_existing_election_by_id
from elections.views.save_election.save_existing_election_json import update_existing_election_from_json
from elections.views.save_nominee.save_new_or_update_existing_nominees import save_new_or_update_existing_nominees
from elections.views.validators.existing_election import validate_nominees_for_existing_election_from_json
from elections.views.validators.validate_from_json import validate_election_date, validate_election_type, \
    validate_and_return_election_json

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
    if JSON_INPUT_FIELD_POST_KEY not in request.POST or ELECTION_ID_POST_KEY not in request.POST:
        context[ERROR_MESSAGES_KEY] = ["Not all necessary fields were detected in your input"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    logger.info(
        "[elections/election_management.py process_existing_election_information_from_json()] "
        "creating new election"
    )
    election_id = request.POST[ELECTION_ID_POST_KEY]
    success, error_messages, updated_elections_information = validate_and_return_election_json(
        request.POST[JSON_INPUT_FIELD_POST_KEY]
    )
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[ERROR_MESSAGES_KEY] = error_messages
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(
            json.dumps(
                request.POST[JSON_INPUT_FIELD_POST_KEY]
            ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
        )
        return render(request, 'elections/update_election/update_election_json.html', context)

    election = _get_existing_election_by_id(election_id)
    if election is None:
        context[ELECTION_ID_POST_KEY] = election_id
        context[ERROR_MESSAGES_KEY] = [
            f"The Selected election for date {updated_elections_information[ELECTION_DATE_POST_KEY]} "
            "does not exist"
        ]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(updated_elections_information)
        return render(request, 'elections/update_election/update_election_json.html', context)
    logger.info(
        f"[elections/election_management.py process_existing_election_information_from_json()] "
        f"updated_elections_information={updated_elections_information}")
    if not (ELECTION_DATE_POST_KEY in updated_elections_information and
            ELECTION_TYPE_POST_KEY in updated_elections_information and
            ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and
            ELECTION_NOMINEES_POST_KEY in updated_elections_information):
        context[ELECTION_ID_POST_KEY] = election_id
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = ["Not all necessary fields were detected in your input"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_election_date(updated_elections_information[ELECTION_DATE_POST_KEY])
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_election_type(updated_elections_information[ELECTION_TYPE_POST_KEY])
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_nominees_for_existing_election_from_json(
        election.id, updated_elections_information[ELECTION_NOMINEES_POST_KEY]
    )
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/update_election/update_election_json.html', context)
    update_existing_election_from_json(
        election,
        updated_elections_information[ELECTION_DATE_POST_KEY],
        updated_elections_information[ELECTION_TYPE_POST_KEY],
        updated_elections_information[ELECTION_WEBSURVEY_LINK_POST_KEY]
    )
    save_new_or_update_existing_nominees(election, updated_elections_information)
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')


