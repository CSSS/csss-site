import json
import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineeLink, NomineePosition
from elections.views.Constants import FINAL_NOMINEE_HTML__NAME, SAVE_NEW_NOMINEE__BUTTON_ID, \
    SAVE_NEW_NOMINEE__BUTTON_ID_VALUE, INPUT_REDIRECT_NOMINEE__NAME, CREATE_OR_UPDATE_NOMINEE__NAME, \
    INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE, SAVE_OR_UPDATE_NOMINEE__VALUE, NOMINEE_DIV__NAME, \
    DRAFT_NOMINEE_HTML__NAME, CURRENT_OFFICER_POSITIONS, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_NOMINEE_SPEECH__NAME, ID_KEY, INPUT_SPEECH_ID__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_POSITION_NAME
from elections.views.create_context.nominee_links.update_nominee.js_functions.on_load_js_functions.\
    create_context_for_main_function_html import \
    create_context_for_main_function_html
from elections.views.create_context.nominee_links.utils.display_errors_html import \
    create_context_for_display_errors_html
from elections.views.create_context.nominee_links.utils.make_context_value_serializable_to_json import \
    make_json_serializable_context_dictionary
from elections.views.extractors.get_nominee__nominee_link import get_election_nominees

logger = logging.getLogger('csss_site')


def create_context_for_create_or_update_nominee__nominee_links_html(context, nominee_link_id=None,
                                                                    error_messages=None,
                                                                    nominee_info=None):
    # nominee_links = NomineeLink.objects.all().filter(id=nominee_link_id)
    # create_new_nominee = not (len(nominee_links) == 1 and nominee_links[0].nominee is not None)
    if nominee_link_id is not None:
        context[FINAL_NOMINEE_HTML__NAME] = get_election_nominees(nominee_link_id)
    create_context_for_display_errors_html(context, error_messages=error_messages)
    _create_context_for_form__nominee_links_html(
        context
    )
    create_context_for_main_function_html(
        context, nominee_link_id=nominee_link_id, nominee_info=nominee_info
    )
    __create_context_for_add_blank_speech_html(context)
    _create_context_for_view_saved_nominee_info_html(context, nominee_link_id=nominee_link_id)
    logger.info(
        "[elections/create_or_update_nominee__nominee_links_html.py"
        " create_context_for_create_or_update_nominee__nominee_links_html()] "
        "context="
    )
    new_context = make_json_serializable_context_dictionary(context)
    logger.info(json.dumps(new_context, indent=3))


def _create_context_for_form__nominee_links_html(context):
    context.update({
        SAVE_NEW_NOMINEE__BUTTON_ID: SAVE_NEW_NOMINEE__BUTTON_ID_VALUE,
        INPUT_REDIRECT_NOMINEE__NAME: CREATE_OR_UPDATE_NOMINEE__NAME,
        INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE: SAVE_OR_UPDATE_NOMINEE__VALUE,
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,

    })


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
