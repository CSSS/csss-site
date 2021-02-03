import json
import logging

from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.views.election_management import JSON_INPUT_FIELD_POST_KEY, TAB_STRING, NOM_NAME_KEY, \
    NOM_POSITION_KEY, NOM_SPEECH_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, NOM_EMAIL_KEY, NOM_DISCORD_USERNAME_KEY,\
    ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, ELECTION_DATE_KEY

logger = logging.getLogger('csss_site')


def show_page_for_user_to_enter_new_election_information_from_json(request):
    """Shows the page where the json is displayed so that the user inputs the data needed to create a new election"""
    logger.info(
        "[elections/election_management.py show_page_for_user_to_enter_new_election_information_from_json()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    if ERROR_MESSAGE_KEY in request.session:
        context[ERROR_MESSAGE_KEY] = request.session[ERROR_MESSAGE_KEY]
        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(request.session[JSON_INPUT_FIELD_POST_KEY])
        del request.session[ERROR_MESSAGE_KEY]
        del request.session[JSON_INPUT_FIELD_POST_KEY]
    else:
        nominee = {NOM_NAME_KEY: "", NOM_POSITION_KEY: [], NOM_SPEECH_KEY: "NONE", NOM_FACEBOOK_KEY: "NONE",
                   NOM_LINKEDIN_KEY: "NONE", NOM_EMAIL_KEY: "NONE", NOM_DISCORD_USERNAME_KEY: "NONE"}

        input_json_context = {ELECTION_TYPE_KEY: "", ELECTION_DATE_KEY: "YYYY-MM-DD HH:MM",
                              ELECTION_WEBSURVEY_LINK_KEY: "",
                              ELECTION_NOMINEES_KEY: [nominee]}

        context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(input_json_context)
    return render(request, 'elections/create_election_json.html', context)
