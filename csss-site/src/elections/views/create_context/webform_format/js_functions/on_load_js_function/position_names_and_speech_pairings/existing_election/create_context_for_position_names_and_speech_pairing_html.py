from about.models import OfficerEmailListAndPositionMapping
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_SPEECH_ID__NAME, CURRENT_OFFICER_POSITIONS, \
    INPUT_NOMINEE_SPEECH__NAME, ID_KEY
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH


def create_context_for_position_names_and_speech_pairing_html(
        nominee_info_position_and_speech_pairing=None, nominee_obj_position_and_speech_pairing=None):
    context = {
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_SPEECH_ID__NAME: ID_KEY,
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH
    }
    nominee_info_in_context = None
    if nominee_info_position_and_speech_pairing is not None:
        # position_names_and_speech_pairing
        nominee_info_in_context = {
            "speech": nominee_info_position_and_speech_pairing.speech,
            "id": nominee_info_position_and_speech_pairing.id,
            "position_names": [nominee_info_position_and_speech_pairing.position_name]
        }
    if nominee_obj_position_and_speech_pairing is not None:
        # position_names_and_speech_pairing
        nominee_info_in_context = {
            "speech": nominee_obj_position_and_speech_pairing.speech,
            "id": nominee_obj_position_and_speech_pairing.id,
            "position_names": [nominee_obj_position_and_speech_pairing.position_name]
        }
    return context, nominee_info_in_context
