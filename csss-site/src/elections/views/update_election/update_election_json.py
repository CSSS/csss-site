import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from elections.models import NomineePosition, Nominee
from elections.views.election_management import TAB_STRING, ELECTION_DICT_POST_KEY, JSON_INPUT_FIELD_POST_KEY, \
    ELECTION_ID_POST_KEY, ELECTION_ID_SESSION_KEY, ELECTION_TYPE_KEY, ELECTION_DATE_KEY, \
    ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, NOM_NAME_KEY, NOM_FACEBOOK_KEY, NOM_SPEECH_KEY, \
    NOM_DISCORD_USERNAME_KEY, NOM_POSITION_KEY, NOM_EMAIL_KEY, NOM_LINKEDIN_KEY, ELECTION_DATE_POST_KEY, \
    ELECTION_TYPE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY
from elections.views.election_management_helper import _get_existing_election_by_id
from elections.views.extractors.extract_from_json import update_existing_election_from_json, save_nominees
from elections.views.validators.validate_from_json import validate_election_date, validate_election_type, \
    validate_new_nominees_for_new_election_from_json, validate_and_return_election_json

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
    return process_existing_election_information_from_json(request, context)


def display_current_election(request, context):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in json form, with possibly an
     error message
    """
    if ELECTION_ID_SESSION_KEY not in request.session:
        context[ERROR_MESSAGES_KEY] = ["Not all necessary fields were detected in your input"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    context[ELECTION_ID_POST_KEY] = request.session[ELECTION_ID_SESSION_KEY]
    del request.session[ELECTION_ID_SESSION_KEY]

    election_dictionary, context[ERROR_MESSAGES_KEY] = \
        _get_information_for_election_user_wants_to_modify(context[ELECTION_ID_POST_KEY])
    context[ELECTION_DICT_POST_KEY] = json.dumps(election_dictionary)
    return render(request, 'elections/update_election/update_election_json.html', context)


def _get_information_for_election_user_wants_to_modify(election_id):
    """Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    election_dictionary -- a JSON representation of the election information and its list of nominees
    error_messages -- potential error message list
    """
    election = _get_existing_election_by_id(election_id)
    if election is None:
        return {}, ["No valid election found for given election id"]
    nominees = [nominee for nominee in Nominee.objects.all().filter(election=election)]
    nominee_positions = []
    for nominee in nominees:
        nominee_positions_names = [
            nominee_position.position_name
            for nominee_position in NomineePosition.objects.all().order_by('position_index')
        ]
        nominee_position = {
            NOM_NAME_KEY: nominee.name, NOM_POSITION_KEY: nominee_positions_names, NOM_EMAIL_KEY: nominee.email,
            NOM_LINKEDIN_KEY: nominee.linked_in, NOM_FACEBOOK_KEY: nominee.facebook,
            NOM_DISCORD_USERNAME_KEY: nominee.discord, NOM_SPEECH_KEY: nominee.speech
        }
        nominee_positions.append(nominee_position)

    election_dictionary = {
        ELECTION_TYPE_KEY: election.election_type, ELECTION_DATE_KEY: election.date.strftime("%Y-%m-%d %H:%M"),
        ELECTION_WEBSURVEY_LINK_KEY: election.websurvey, ELECTION_NOMINEES_KEY: nominee_positions
    }

    return election_dictionary, None


def process_existing_election_information_from_json(request, context):
    """Updates the specified election using the JSON input"""
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
        context[ELECTION_DICT_POST_KEY] = json.dumps(
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
        context[ELECTION_DICT_POST_KEY] = json.dumps(updated_elections_information)
        return render(request, 'elections/update_election/update_election_json.html', context)
    logger.info(
        f"[elections/election_management.py process_existing_election_information_from_json()] "
        f"updated_elections_information={updated_elections_information}")
    if not (ELECTION_DATE_POST_KEY in updated_elections_information and
            ELECTION_TYPE_POST_KEY in updated_elections_information and
            ELECTION_WEBSURVEY_LINK_POST_KEY in updated_elections_information and
            ELECTION_NOMINEES_POST_KEY in updated_elections_information):
        context[ELECTION_ID_POST_KEY] = election_id
        context[ELECTION_DICT_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = ["Not all necessary fields were detected in your input"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_election_date(updated_elections_information[ELECTION_DATE_POST_KEY])
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[ELECTION_DICT_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_election_type(updated_elections_information[ELECTION_TYPE_POST_KEY])
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[ELECTION_DICT_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/update_election/update_election_json.html', context)
    success, error_message = validate_new_nominees_for_new_election_from_json(
        updated_elections_information[ELECTION_NOMINEES_POST_KEY]
    )
    if not success:
        context[ELECTION_ID_POST_KEY] = election_id
        context[ELECTION_DICT_POST_KEY] = json.dumps(updated_elections_information)
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/update_election/update_election_json.html', context)
    update_existing_election_from_json(
        election,
        updated_elections_information[ELECTION_DATE_POST_KEY],
        updated_elections_information[ELECTION_TYPE_POST_KEY],
        updated_elections_information[ELECTION_WEBSURVEY_LINK_POST_KEY]
    )
    save_nominees(election, updated_elections_information)
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')
