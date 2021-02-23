import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.election_management import JSON_INPUT_FIELD_POST_KEY, TAB_STRING, NOM_NAME_KEY, \
    NOM_POSITION_KEY, NOM_SPEECH_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, NOM_EMAIL_KEY, NOM_DISCORD_USERNAME_KEY, \
    ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, ELECTION_DATE_KEY, \
    ELECTION_TYPE_POST_KEY, ELECTION_DATE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY, \
    NOM_POSITION_AND_SPEECH_KEY
from elections.views.extractors.extract_from_json import save_new_election_from_json
from elections.views.validators.validate_from_json import validate_and_return_election_json, validate_election_type, \
    validate_election_date, \
    validate_new_nominees_for_new_election_from_json

logger = logging.getLogger('csss_site')


def display_and_process_html_for_new_json_election(request):
    """Shows the page where the json is displayed so that the user inputs the data needed to create a new election"""
    logger.info(
        "[elections/show_page_for_user_input.py display_and_process_html_for_new_json_election()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    context['types_of_elections'] = f"Options for \"{ELECTION_TYPE_KEY}\": {', '.join(valid_election_type_choices)}"
    current_positions = [
        position.position_name for position in OfficerEmailListAndPositionMapping.objects.all().filter(
            marked_for_deletion=False
        )
    ]
    context['valid_position_names'] = f"Valid Positions: {', '.join(current_positions)}"

    if request.method != "POST":
        return display_empty_election_json(request, context)
    return process_new_inputted_election(request, context)


def display_empty_election_json(request, context):
    context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(
        {
            ELECTION_TYPE_KEY: "", ELECTION_DATE_KEY: "YYYY-MM-DD HH:MM",
            ELECTION_WEBSURVEY_LINK_KEY: "",
            ELECTION_NOMINEES_KEY: [
                {
                    NOM_NAME_KEY: "",
                    NOM_POSITION_AND_SPEECH_KEY: [{NOM_POSITION_KEY: [], NOM_SPEECH_KEY: "NONE"}],
                    NOM_FACEBOOK_KEY: "NONE", NOM_LINKEDIN_KEY: "NONE", NOM_EMAIL_KEY: "NONE",
                    NOM_DISCORD_USERNAME_KEY: "NONE"
                 }
            ]
        }
    )
    return render(request, 'elections/create_election/create_election_json.html', context)


def process_new_inputted_election(request, context):
    if JSON_INPUT_FIELD_POST_KEY not in request.POST:
        error_message = "Could not find the json in the input"
        logger.info("[elections/validate_from_json.py validate_inputted_election_json()] "
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
            f"[elections/validate_from_json.py validate_inputted_election_json()] {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_type(election_json[ELECTION_TYPE_POST_KEY])
    if not success:
        context[ERROR_MESSAGES_KEY] = error_messages
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
        return render(request, 'elections/create_election/create_election_json.html', context)

    success, error_message = validate_election_date(election_json[ELECTION_DATE_POST_KEY])
    if not success:
        context[ERROR_MESSAGES_KEY] = error_messages
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
