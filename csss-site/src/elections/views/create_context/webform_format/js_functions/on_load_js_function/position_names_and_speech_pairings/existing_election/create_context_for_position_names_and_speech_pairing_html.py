from about.models import OfficerEmailListAndPositionMapping
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_SPEECH_ID__NAME, CURRENT_OFFICER_POSITIONS, \
    INPUT_NOMINEE_SPEECH__NAME, ID_KEY, NEW_WEBFORM_ELECTION__HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_POSITION_NAME, ELECTION_JSON_KEY__NOMINEES


def create_context_for_position_names_and_speech_pairing_html(
        context, nominee_info_to_add_to_context=None, nominee_info=None, speech_obj=None,
        speech_ids=None, nominee_obj=None, new_webform_election=True):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform/js_functions/on_load_js_function/
     position_names_and_speech_pairings/existing_election/position_names_and_speech_pairing.html

    context -- the context dictionary that has to be populated for the position_names_and_speech_pairing.html
    nominee_info_to_add_to_context -- the nominee info that is being constructed for current nominee that needs to be
     added to the context dictionary
    nominees_info -- the nominee info that the user inputted, otherwise None
    new_webform_election -- bool to indicate if the election is a new webform election
    """
    context.update({
        NEW_WEBFORM_ELECTION__HTML__NAME: new_webform_election,
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
    if nominee_info is not None and speech_obj is None:
        if new_webform_election:
            # POST /elections/new_election_webform
            nominee_info_to_add_to_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
            if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee_info and type(nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]) is list:  # noqa: E501
                for speech_and_position_pairing in nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]:
                    new_speech_and_position_pairing = {
                        ELECTION_JSON_KEY__NOM_SPEECH: speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH]
                    }
                    if ELECTION_JSON_KEY__NOM_POSITION_NAMES in speech_and_position_pairing:
                        new_speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]  # noqa: E501
                    nominee_info_to_add_to_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].append(
                        new_speech_and_position_pairing
                    )
        else:
            # POST /elections/<slug>/election_modification_webform/
            nominee_info_to_add_to_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
            if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee_info and type(nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]) is list:  # noqa: E501
                for speech_and_position_pairing in nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]:
                    new_speech_and_position_pairing = {
                        ELECTION_JSON_KEY__NOM_SPEECH: speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH]
                    }
                    if ID_KEY in speech_and_position_pairing:
                        new_speech_and_position_pairing[ID_KEY] = speech_and_position_pairing[ID_KEY]
                    if ELECTION_JSON_KEY__NOM_POSITION_NAMES in speech_and_position_pairing:
                        new_speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]  # noqa: E501
                    nominee_info_to_add_to_context[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].append(
                        new_speech_and_position_pairing
                    )
    elif speech_obj is not None and nominee_info is None:
        # GET /elections/<slug>/election_modification_webform/
        if speech_ids is None:
            speech_ids = []
        if speech_obj.id not in speech_ids:
            speech_and_position_pairings = []
            speech_and_position_pairing = {}
            speech_ids.append(speech_obj.id)
            for nominee_position in speech_obj.nomineeposition_set.all():
                if ELECTION_JSON_KEY__NOM_POSITION_NAMES not in speech_and_position_pairing:
                    speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = [{
                        ID_KEY: nominee_position.id,
                        ELECTION_JSON_KEY__NOM_POSITION_NAME: nominee_position.position_name
                    }]
                else:
                    speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES].append(
                        {
                            ID_KEY: nominee_position.id,
                            ELECTION_JSON_KEY__NOM_POSITION_NAME: nominee_position.position_name
                        }
                    )
            speech_and_position_pairing[ID_KEY] = speech_obj.id
            speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH] = speech_obj.speech
            if speech_and_position_pairing is not None:
                speech_and_position_pairings.append(speech_and_position_pairing)
            nominee_info_to_add_to_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].extend(  # noqa: E501
                speech_and_position_pairings
            )
