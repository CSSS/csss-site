from about.models import OfficerEmailListAndPositionMapping
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_SPEECH_ID__NAME, CURRENT_OFFICER_POSITIONS, \
    INPUT_NOMINEE_SPEECH__NAME, ID_KEY, NEW_ELECTION_OR_NOMINEE__HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_POSITION_NAME, ELECTION_JSON_KEY__NOMINEES


def create_context_for_position_names_and_speech_pairing_html(
        context, nominee_info_to_add_to_context=None, nominee_info=None, speech_obj=None,
        speech_ids=None, nominee_name=None, new_election_or_nominee=True, populate_nominee_info=False):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform/js_functions/on_load_js_function/
     position_names_and_speech_pairings/existing_election/position_names_and_speech_pairing.html

    context -- the context dictionary that has to be populated for the position_names_and_speech_pairing.html
    nominee_info_to_add_to_context -- the nominee info that is being constructed for current nominee that needs to be
     added to the context dictionary
    nominee_info -- the nominee info that the user inputted, otherwise None
    speech_obj -- the object for the speech that has to be added to the context
    speech_ids -- keeps tracks of the speech_ids attached to the context so far
    nominee_name -- the saved nominee's name
    new_election_or_nominee -- bool to indicate if the election or nominee is new
    populate_nominee_info -- flag to indicate whether or not to populate the nominee_info when being called via
     create_context_for_update_election__webform_html context creator
    """

    context.update({
        NEW_ELECTION_OR_NOMINEE__HTML__NAME: new_election_or_nominee,
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
    if populate_nominee_info:
        if nominee_info is not None:
            # POST /elections/new_election_webform
            # POST /elections/<slug>/election_modification_webform/
            # POST /elections/create_or_update_via_nominee_links/?nominee_link_id=<nominee_link_id>
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
        elif speech_obj is not None:
            # GET /elections/<slug>/election_modification_webform/
            # GET /elections/create_or_update_via_nominee_links/?nominee_link_id=<nominee_link_id>
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
                nominee_info_to_add_to_context[nominee_name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].extend(  # noqa: E501
                    speech_and_position_pairings
                )
