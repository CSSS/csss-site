import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from elections.models import Election, NomineePosition
from elections.views.election_management import TAB_STRING, ELECTION_DICT_POST_KEY, JSON_INPUT_FIELD_POST_KEY, \
    ELECTION_ID_POST_KEY, ELECTION_ID_SESSION_KEY, ELECTION_TYPE_KEY, ELECTION_DATE_KEY, \
    ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, NOM_NAME_KEY, NOM_FACEBOOK_KEY, NOM_SPEECH_KEY, \
    NOM_DISCORD_USERNAME_KEY, NOM_POSITION_KEY, NOM_EMAIL_KEY, NOM_LINKEDIN_KEY, ELECTION_DATE_POST_KEY, \
    ELECTION_TYPE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY
from elections.views.election_management_helper import _get_existing_election_by_id, \
    _update_information_for_existing_election_from_json, \
    _validate_nominee_information_for_existing_elections_from_json_and_save_all_changes

logger = logging.getLogger('csss_site')


def display_and_process_html_for_modification_of_json_election(request):
    """
    Shows the requested election to the user in JSON format
    """
    logger.info(
        f"[administration/election_management.py show_page_for_user_to_modify_election_information_from_json()] "
        f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if request.method != "POST":
        return display_current_election(request, context)
    return process_existing_election_information_from_json(request)


def display_current_election(request, context):
    if ELECTION_ID_SESSION_KEY not in request.session:
        context[ERROR_MESSAGES_KEY] = ["Not all necessary fields were detected in your input"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    election_id = request.session[ELECTION_ID_SESSION_KEY]
    context[ELECTION_DICT_POST_KEY] = json.dumps(
        _get_information_for_election_user_wants_to_modify(
            election_id
        )
    )
    context[ELECTION_ID_POST_KEY] = election_id
    del request.session[ELECTION_ID_SESSION_KEY]
    return render(request, 'elections/update_election/update_election_json.html', context)


def _get_information_for_election_user_wants_to_modify(election_id):
    """Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    election_dictionary -- a JSON representation of the election information and its list of nominees
    """
    election = Election.objects.get(id=election_id)
    current_position_mappings = [mapping for mapping in OfficerEmailListAndPositionMapping.objects.all()]
    current_position_mappings.sort(key=lambda x: x.position_index)
    nominee_positions = []
    nominee_position_that_are_also_current_positions = []
    for current_position_mapping in current_position_mappings:
        nominee_position_that_are_also_current_positions.append(current_position_mapping.position_name)
        nominee_positions.extend(
            [
                position for position in
                NomineePosition.objects.all().filter(nominee__election=election,
                                                     position_name=current_position_mapping.position_name)
            ]
        )
    nominee_positions.extend(
        [
            position for position in
            NomineePosition.objects.all().filter(nominee__election=election)
            if position.position_name not in nominee_position_that_are_also_current_positions
        ]
    )

    election_dictionary = {
        ELECTION_TYPE_KEY: election.election_type, ELECTION_DATE_KEY: election.date.strftime("%Y-%m-%d %H:%M"),
        ELECTION_WEBSURVEY_LINK_KEY: election.websurvey, ELECTION_NOMINEES_KEY: []
    }
    for nominee_position in nominee_positions:
        nominee = nominee_position.nominee
        election_dictionary[ELECTION_NOMINEES_KEY].append(
            {
                NOM_NAME_KEY: nominee.name, NOM_POSITION_KEY: nominee_position.position_name,
                NOM_EMAIL_KEY: nominee.email, NOM_LINKEDIN_KEY: nominee.linked_in,
                NOM_FACEBOOK_KEY: nominee.facebook, NOM_DISCORD_USERNAME_KEY: nominee.discord,
                NOM_SPEECH_KEY: nominee.speech
            }
        )

    return election_dictionary


def process_existing_election_information_from_json(request):
    """Updates the specified election using the JSON input"""
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if JSON_INPUT_FIELD_POST_KEY in request.POST and ELECTION_ID_POST_KEY in request.POST:
        logger.info(
            "[elections/election_management.py process_existing_election_information_from_json()] "
            "creating new election"
        )
        election_id = request.POST[ELECTION_ID_POST_KEY]
        try:
            updated_elections_information = json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY])
        except json.decoder.JSONDecodeError as e:
            logger.info(
                "[elections/election_management.py process_existing_election_information_from_json()] "
                "experienced an error trying to interpet the json input from the user"
            )
            request.session[ERROR_MESSAGE_KEY] = f"Unable to decode the JSON input: {e}"
            request.session[JSON_INPUT_FIELD_POST_KEY] = json.dumps(
                request.POST[JSON_INPUT_FIELD_POST_KEY]
            ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
            request.session[ELECTION_ID_SESSION_KEY] = election_id
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_json")
        election = _get_existing_election_by_id(election_id)
        if election is None:
            request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(
                f"The Selected election for date {updated_elections_information[ELECTION_DATE_POST_KEY]} "
                "does not exist"
            )
            request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
            request.session[ELECTION_ID_SESSION_KEY] = election_id
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_json")
        logger.info(
            f"[elections/election_management.py process_existing_election_information_from_json()] "
            f"updated_elections_information={updated_elections_information}")
        if ELECTION_DATE_POST_KEY in updated_elections_information and \
                ELECTION_TYPE_POST_KEY in updated_elections_information and \
                ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and \
                ELECTION_NOMINEES_POST_KEY in updated_elections_information:
            success, election, error_message = _update_information_for_existing_election_from_json(
                election, updated_elections_information)
            if not success:
                request.session[ERROR_MESSAGE_KEY] = error_message
                request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
                request.session[ELECTION_ID_SESSION_KEY] = election_id
                return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_json")
            success, error_message = \
                _validate_nominee_information_for_existing_elections_from_json_and_save_all_changes(
                    election, updated_elections_information[ELECTION_NOMINEES_POST_KEY])
            if not success:
                request.session[ERROR_MESSAGE_KEY] = error_message
                request.session[JSON_INPUT_FIELD_POST_KEY] = updated_elections_information
                request.session[ELECTION_ID_SESSION_KEY] = election_id
                return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_json")
            return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')
    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Not all necessary fields were detected in your input")
    return render_value
