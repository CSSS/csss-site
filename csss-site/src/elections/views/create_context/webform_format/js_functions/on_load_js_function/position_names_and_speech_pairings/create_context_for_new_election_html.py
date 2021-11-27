from about.models import OfficerEmailListAndPositionMapping
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_NOMINEE_SPEECH__NAME, CURRENT_OFFICER_POSITIONS, DRAFT_NOMINEE_HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH


def create_context_for_new_election_html(context, nominee_obj=None, nominee_info=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,

        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ]
    })
    if nominee_info is not None:
        context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = [
            create_position_names_and_speech_pairing_for_nominee(nominee_info=position_names_and_speech_pairing)
            for position_names_and_speech_pairing in nominee_info[ELECTION_JSON_KEY__NOM_POSITION_NAMES]
        ]
    elif nominee_obj is not None:
        context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = [
            create_position_names_and_speech_pairing_for_nominee(nominee_obj=position_names_and_speech_pairing)
            for position_names_and_speech_pairing in nominee_obj[ELECTION_JSON_KEY__NOM_POSITION_NAMES]
        ]


def create_position_names_and_speech_pairing_for_nominee(nominee_info=None, nominee_obj=None):
    if nominee_info is not None:
        return {
            ELECTION_JSON_KEY__NOM_POSITION_NAMES: nominee_info[ELECTION_JSON_KEY__NOM_POSITION_NAMES],
            ELECTION_JSON_KEY__NOM_SPEECH: nominee_info[ELECTION_JSON_KEY__NOM_SPEECH]
        }
    elif nominee_obj is not None:
        return {
            ELECTION_JSON_KEY__NOM_POSITION_NAMES: nominee_obj[ELECTION_JSON_KEY__NOM_POSITION_NAMES],
            ELECTION_JSON_KEY__NOM_SPEECH: nominee_obj[ELECTION_JSON_KEY__NOM_SPEECH]
        }
