import json
import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineeLink, NomineePosition
from elections.views.Constants import FINAL_NOMINEE_HTML__NAME, SAVE_NEW_NOMINEE__BUTTON_ID, \
    SAVE_NEW_NOMINEE__BUTTON_ID_VALUE, INPUT_REDIRECT_NOMINEE__NAME, CREATE_OR_UPDATE_NOMINEE__NAME, \
    INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE, SAVE_OR_UPDATE_NOMINEE__VALUE, NOMINEE_DIV__NAME, ELECTION_JSON_KEY__NOMINEE, \
    INPUT_NOMINEE_NAME__NAME, ELECTION_JSON_KEY__NOM_NAME, INPUT_NOMINEE_FACEBOOK__NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, INPUT_NOMINEE_LINKEDIN__NAME, ELECTION_JSON_KEY__NOM_LINKEDIN, \
    INPUT_NOMINEE_EMAIL__NAME, ELECTION_JSON_KEY__NOM_EMAIL, INPUT_NOMINEE_DISCORD__NAME, \
    ELECTION_JSON_KEY__NOM_DISCORD, CREATE_NEW_NOMINEE__HTML_NAME, DRAFT_NOMINEE_HTML__NAME, CURRENT_OFFICER_POSITIONS, \
    INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, ELECTION_JSON_KEY__NOM_POSITION_NAMES, INPUT_NOMINEE_SPEECH__NAME, \
    ELECTION_JSON_KEY__NOM_SPEECH, ID_KEY, ELECTION_JSON_KEY__NOM_POSITION_NAME, INPUT_SPEECH_ID__NAME
from elections.views.create_context.nominee_links.utils.display_errors_html import \
    create_context_for_display_errors_html
from elections.views.create_context.nominee_links.utils.make_context_value_serializable_to_json import \
    make_context_value_json_serializable
from elections.views.extractors.get_nominee__nominee_link import get_election_nominees

logger = logging.getLogger('csss_site')


def create_context_for_update_nominee__nominee_links_html(context, nominee_link_id=None, error_messages=None,
                                                          nominee_info=None):
    nominee_links = NomineeLink.objects.all().filter(id=nominee_link_id)
    create_new_nominee = not (len(nominee_links) == 1 and nominee_links[0].nominee is not None)
    if nominee_link_id is not None:
        context[FINAL_NOMINEE_HTML__NAME] = get_election_nominees(nominee_link_id)
    create_context_for_display_errors_html(context, error_messages=error_messages)
    _create_context_for_form__nominee_links_html(
        context
    )
    _create_context_for_main_function_html(
        context, nominee_link_id=nominee_link_id, create_new_nominee=create_new_nominee, nominee_info=nominee_info
    )
    __create_context_for_add_blank_speech_html(context)
    _create_context_for_view_saved_nominee_info_html(context, nominee_link_id=nominee_link_id)
    logger.info(
        "[elections/create_nominee_links_context.py"
        " create_context_for_update_nominee__nominee_links_html()] "
        "context="
    )
    new_context = {key: make_context_value_json_serializable(value) for (key, value) in context.items()}
    logger.info(json.dumps(new_context, indent=3))


def _create_context_for_form__nominee_links_html(context):
    context.update({
        SAVE_NEW_NOMINEE__BUTTON_ID: SAVE_NEW_NOMINEE__BUTTON_ID_VALUE,
        INPUT_REDIRECT_NOMINEE__NAME: CREATE_OR_UPDATE_NOMINEE__NAME,
        INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE: SAVE_OR_UPDATE_NOMINEE__VALUE,
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,

    })


def _create_context_for_main_function_html(
        context, nominee_link_id=None, create_new_nominee=False,
        nominee_info=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_NAME__NAME: ELECTION_JSON_KEY__NOM_NAME,
        INPUT_NOMINEE_FACEBOOK__NAME: ELECTION_JSON_KEY__NOM_FACEBOOK,
        INPUT_NOMINEE_LINKEDIN__NAME: ELECTION_JSON_KEY__NOM_LINKEDIN,
        INPUT_NOMINEE_EMAIL__NAME: ELECTION_JSON_KEY__NOM_EMAIL,
        INPUT_NOMINEE_DISCORD__NAME: ELECTION_JSON_KEY__NOM_DISCORD,
        CREATE_NEW_NOMINEE__HTML_NAME: create_new_nominee,
    })
    nominee_link = NomineeLink.objects.get(id=nominee_link_id)
    nominee_obj = nominee_link.nominee if nominee_link.nominee is not None else None

    if nominee_info is not None:
        context.update(
            {
                DRAFT_NOMINEE_HTML__NAME: {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_info[ELECTION_JSON_KEY__NOM_NAME],
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK],
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN],
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_info[ELECTION_JSON_KEY__NOM_EMAIL],
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_info[ELECTION_JSON_KEY__NOM_DISCORD]
                }
            }
        )
    elif nominee_obj is not None:
        context.update(
            {
                DRAFT_NOMINEE_HTML__NAME: {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_obj.name,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_obj.facebook,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_obj.linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_obj.email,
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_obj.discord
                }
            }
        )
    _create_context_for_new_nominee_html(context, nominee_info=nominee_info)
    _create_context_for_existing_nominee_html(context, nominee_info=nominee_info, nominee_obj=nominee_obj)


def __create_context_for_add_blank_speech_html(context):
    context.update({
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
    })


def _create_context_for_view_saved_nominee_info_html(context, nominee_link_id=None):
    if nominee_link_id is not None:
        context[FINAL_NOMINEE_HTML__NAME] = get_election_nominees(nominee_link_id)


def _create_context_for_new_nominee_html(context, nominee_info=None):
    if nominee_info is not None:
        context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = \
            nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
    })


def _create_context_for_existing_nominee_html(context, nominee_info=None, nominee_obj=None):
    if nominee_info is None and nominee_obj is not None:
        positions = NomineePosition.objects.all().filter(
            nominee_speech__nominee_id=nominee_obj.id
        ).order_by('position_index')
        pairings = {}
        for position in positions:
            speech_id = position.nominee_speech.id
            if speech_id in pairings:
                pairings[speech_id][ELECTION_JSON_KEY__NOM_POSITION_NAMES].append({
                    ID_KEY: position.id,
                    ELECTION_JSON_KEY__NOM_POSITION_NAME: position.position_name
                })
            else:
                pairings[speech_id] = {
                    ELECTION_JSON_KEY__NOM_SPEECH: position.nominee_speech.speech,
                    ID_KEY: speech_id,
                    ELECTION_JSON_KEY__NOM_POSITION_NAMES: [{
                        ID_KEY: position.id,
                        ELECTION_JSON_KEY__NOM_POSITION_NAME: position.position_name
                    }]
                }
        if DRAFT_NOMINEE_HTML__NAME not in context:
            context[DRAFT_NOMINEE_HTML__NAME] = {}
        context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = \
            list(pairings.values())
    context.update({
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        INPUT_SPEECH_ID__NAME: ID_KEY,
    })
