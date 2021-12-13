from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineePosition
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_SPEECH_ID__NAME, CURRENT_OFFICER_POSITIONS, \
    INPUT_NOMINEE_SPEECH__NAME, ID_KEY, NEW_WEBFORM_ELECTION__HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_POSITION_NAME, ELECTION_JSON_KEY__NOMINEES


def create_context_for_position_names_and_speech_pairing_html(
        context, nominee_info_to_add_to_context=None, nominee_info=None,


        nominee_info_for_context=None, nominee_info_position_and_speech_pairing=None,
        speech_obj=None, speech_ids=None,
        nominee_obj=None,new_webform_election=True):
    context.update({
        NEW_WEBFORM_ELECTION__HTML__NAME : new_webform_election,
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEES,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        INPUT_SPEECH_ID__NAME: ID_KEY,

    })
    if nominee_info is not None:
        # creating a new webform election
        nominee_info_to_add_to_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
        if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee_info and type(nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]) is list:
            for speech_and_position_pairing in nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]:
                nominee_info_to_add_to_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].append({
                    ELECTION_JSON_KEY__NOM_SPEECH: speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH],
                    ELECTION_JSON_KEY__NOM_POSITION_NAMES: speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]
                })
    # elif speech_obj is not None:
    #     if speech_ids is None:
    #         speech_ids = []
    #     if speech_obj.id not in speech_ids:
    #         speech_and_position_pairings = []
    #         speech_and_position_pairing = {}
    #         speech_ids.append(speech_obj.id)
    #         for position_name in NomineePosition.objects.all().filter(nominee_speech=speech_obj).order_by(
    #                 'position_index'
    #         ):
    #             if ELECTION_JSON_KEY__NOM_POSITION_NAMES not in speech_and_position_pairing:
    #                 speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = [{
    #                     ID_KEY: position_name.id,
    #                     ELECTION_JSON_KEY__NOM_POSITION_NAME: position_name.position_name
    #                 }]
    #             else:
    #                 speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES].append(
    #                     {
    #                         ID_KEY: position_name.id,
    #                         ELECTION_JSON_KEY__NOM_POSITION_NAME: position_name.position_name
    #                     }
    #                 )
    #         speech_and_position_pairing[ID_KEY] = speech_obj.id
    #         speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH] = speech_obj.speech
    #         if speech_and_position_pairing is not None:
    #             speech_and_position_pairings.append(speech_and_position_pairing)
    #         nominee_info_for_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].extend(
    #             speech_and_position_pairings
    #         )