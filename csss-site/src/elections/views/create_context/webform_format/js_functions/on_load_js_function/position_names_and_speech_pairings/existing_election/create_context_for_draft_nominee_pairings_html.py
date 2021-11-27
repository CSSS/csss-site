from elections.views.Constants import DRAFT_NOMINEE_HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS
from elections.views.create_context.webform_format.js_functions.on_load_js_function.position_names_and_speech_pairings.existing_election.create_context_for_position_names_and_speech_pairing_html import \
    create_context_for_position_names_and_speech_pairing_html


def create_context_for_draft_nominee_pairings_html(context, nominee_info=None):
    if nominee_info is not None:
        context_from_position_names_and_speech_pairing_html, context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = \
            create_context_for_position_names_and_speech_pairing_html(nominee_info_position_and_speech_pairing=nominee_info[speech_pairing])
        context.update(context_from_position_names_and_speech_pairing_html)

