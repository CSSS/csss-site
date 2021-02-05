import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.create_new_election_with_json.extraction.extract_from_json import save_new_election, \
    save_new_election_from_json
from elections.views.create_new_election_with_json.validation.validate_from_json import validate_inputted_election_json
from elections.views.election_management import JSON_INPUT_FIELD_POST_KEY, TAB_STRING, NOM_NAME_KEY, \
    NOM_POSITION_KEY, NOM_SPEECH_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, NOM_EMAIL_KEY, NOM_DISCORD_USERNAME_KEY, \
    ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, ELECTION_DATE_KEY

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
        position.position_name for position in OfficerEmailListAndPositionMapping.objects.all()
    ]
    context['valid_position_names'] = f"Valid Positions: {', '.join(current_positions)}"

    if request.method == "POST":
        success, error_messages, election_json = validate_inputted_election_json(request)
        if not success:
            context[ERROR_MESSAGES_KEY] = error_messages
            context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_json)
            return render(request, 'elections/create_election_json.html', context)

        election_slug = save_new_election_from_json(
            json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY])
        )
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election_slug}/')
    context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(
        {
            ELECTION_TYPE_KEY: "", ELECTION_DATE_KEY: "YYYY-MM-DD HH:MM",
            ELECTION_WEBSURVEY_LINK_KEY: "",
            ELECTION_NOMINEES_KEY: [
                {NOM_NAME_KEY: "", NOM_POSITION_KEY: [], NOM_SPEECH_KEY: "NONE", NOM_FACEBOOK_KEY: "NONE",
                 NOM_LINKEDIN_KEY: "NONE", NOM_EMAIL_KEY: "NONE", NOM_DISCORD_USERNAME_KEY: "NONE"}
            ]
        }
    )
    return render(request, 'elections/create_election_json.html', context)
