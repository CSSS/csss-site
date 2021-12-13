from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineeSpeech, NomineePosition
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_NOMINEE_SPEECH__NAME, CURRENT_OFFICER_POSITIONS, \
    ID_KEY
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__NOM_POSITION_NAME


def create_context_for_new_election_html(context, nominee_info_for_context=None, nominee_obj=None, nominee_info=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEES,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,

        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ]
    })
    if nominee_info is not None and nominee_info_for_context is not None:
        nominee_info_for_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
        if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee_info:
            for position_names_and_speech_pairing in nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]:
                nominee_speech_position_pairing_for_context = {}
                if ELECTION_JSON_KEY__NOM_SPEECH in position_names_and_speech_pairing:
                    nominee_speech_position_pairing_for_context[ELECTION_JSON_KEY__NOM_SPEECH] = \
                        position_names_and_speech_pairing[ELECTION_JSON_KEY__NOM_SPEECH]
                if ELECTION_JSON_KEY__NOM_POSITION_NAMES in position_names_and_speech_pairing:
                    nominee_speech_position_pairing_for_context[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = \
                        position_names_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]
                nominee_info_for_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].append(
                    nominee_speech_position_pairing_for_context
                )
    elif nominee_obj is not None:
        speech_and_position_pairings = []
        speech_ids = []
        nominee_info_for_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
        for speech in NomineeSpeech.objects.all().filter(nominee=nominee_obj).order_by(
                'nomineeposition__position_index'
        ):
            speech_and_position_pairing = {}
            if speech.id not in speech_ids:
                speech_ids.append(speech.id)
                for position_name in NomineePosition.objects.all().filter(nominee_speech=speech).order_by(
                    'position_index'
                ):
                    if ELECTION_JSON_KEY__NOM_POSITION_NAMES not in speech_and_position_pairing:
                        speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = [{
                            ID_KEY: position_name.id,
                            ELECTION_JSON_KEY__NOM_POSITION_NAMES:position_name.position_name
                        }]
                    else:
                        speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES].append(
                            {
                                ID_KEY: position_name.id,
                                ELECTION_JSON_KEY__NOM_POSITION_NAME : position_name.position_name
                            }
                        )
                speech_and_position_pairing[ID_KEY] = speech.id
                speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH] = speech.speech
                if speech_and_position_pairing is not None:
                    speech_and_position_pairings.append(speech_and_position_pairing)
        nominee_info_for_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].extend(
            speech_and_position_pairings
        )