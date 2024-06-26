from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries, validate_markdown
from elections.models import NomineeSpeech, NomineePosition
from elections.views.Constants import ID_KEY
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_SPEECH, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_JSON_KEY__NOM_POSITION_NAME


def validate_speech_in_pairing(speech_ids_so_far, speech_and_position_pairing, election_id, full_name):
    """
    Ensures that the pairing has a speeh and if there is an ID, it does belong to ths specified election

    Keyword Argument
    speech_and_position_pairing -- the dict that contains the speech
    election_id -- the ID for the election that the speech belongs to
    name -- the name of the nominee that the speech belongs to

    Return
    Bool -- true or false depending on if the speech and [potential] ID is valid
    error_message -- an error message if the validation failed, or None otherwise
    """
    if not (ELECTION_JSON_KEY__NOM_SPEECH in speech_and_position_pairing):
        return False, f"one of the speech/position pairings is missing a speech for nominee {full_name}"
    if not (ELECTION_JSON_KEY__NOM_SPEECH in speech_and_position_pairing and
            len(speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH]) > 0):
        return False, f"one of the speeches specified for {full_name} is invalid"
    sucess, error_message = validate_markdown(
        speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH]
    )
    if not sucess:
        return sucess, error_message
    if ID_KEY in speech_and_position_pairing:
        validate_id_for_speech_pairing(speech_ids_so_far, speech_and_position_pairing, election_id)
    return True, None


def validate_id_for_speech_pairing(speech_ids_so_far, speech_and_position_pairing, election_id):
    """
    returns a Bool that indicates if the ID in the speech_and_position_pairing is valid and belongs to a speech
     in the current election

    Keyword Argument
    speech_and_position_pairing -- the dict that contains the ID for the speech
    election_id -- the Id for the election to check if the speech belongs to it
    """
    if len(
        NomineeSpeech.objects.all().filter(
            id=int(speech_and_position_pairing[ID_KEY]), nominee__election_id=election_id
        )
    ) != 1:
        # if the ID does not map to a current Speech object
        del speech_and_position_pairing[ID_KEY]
    else:
        if int(speech_and_position_pairing[ID_KEY]) in speech_ids_so_far:
            del speech_and_position_pairing[ID_KEY]
        else:
            speech_ids_so_far.append(int(speech_and_position_pairing[ID_KEY]))


def validate_position_in_pairing(position_ids_so_far, speech_and_position_pairing, specified_position_names,
                                 election_id, full_name):
    """
    Ensures that the position is valid

    Keyword Argument
    speech_and_position_pairing -- the dict that contains the list of positions
    specified_position_names -- the position names that have been specified so far
    election_id -- the ID for the election that the position name belongs to
    name -- the name of the nominee that is running for the specified position names

    Return
    Bool -- true or false depending on if the validation of the position and possible ID passed
    error_message -- error message if the validation is False, None otherwise
    """
    if ELECTION_JSON_KEY__NOM_POSITION_NAMES not in speech_and_position_pairing:
        return False, f"positions are not specified for one of the speeches for nominee {full_name}"
    if not there_are_multiple_entries(speech_and_position_pairing, ELECTION_JSON_KEY__NOM_POSITION_NAMES):
        return False, f"It seems that the nominee {full_name} does not have a list of positions " \
                      f"for one of the positions they are running for"
    for position in speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]:
        if type(position) is dict:
            if ID_KEY in position:
                validate_id_for_position_pairing(position_ids_so_far, position, election_id)
            if not (ELECTION_JSON_KEY__NOM_POSITION_NAME in position):
                return False, f"No position name[s] found for one of the speeches for nominee {full_name}"
            position_name = position[ELECTION_JSON_KEY__NOM_POSITION_NAME]
        else:
            position_name = position
        if not validate_position_name(position_name):
            return False, f"Detected invalid position of {position_name} for nominee {full_name}"
        if position_name in specified_position_names:
            return False, f"the nominee {full_name} has the position {position_name} specified more than once"
        specified_position_names.append(position_name)
    return True, None


def validate_id_for_position_pairing(position_ids_so_far, position_dict, election_id):
    """
    returns a Bool that indicates if the ID in the position_dict is valid and belongs to a position name
     in the current election

    Keyword Argument
    position_dict -- the dict that contains the ID for the position_name
    election_id -- the Id for the election to check if the position_name belongs to it
    """
    if not f"{position_dict[ID_KEY]}".isdigit():
        del position_dict[ID_KEY]
    else:
        if len(
            NomineePosition.objects.all().filter(
                id=int(position_dict[ID_KEY]), nominee_speech__nominee__election_id=election_id
            )
        ) != 1:
            del position_dict[ID_KEY]
        else:
            if int(position_dict[ID_KEY]) in position_ids_so_far:
                del position_dict[ID_KEY]
            else:
                position_ids_so_far.append(int(position_dict[ID_KEY]))


def validate_position_name(position_name):
    """
    returns a Bool that indicates if the position name is for a CSSS position that is elected via an election officer

    Keyword Argument
    position_name -- the name of the position
    """
    return len(
        OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=position_name, marked_for_deletion=False, elected_via_election_officer=True
        )
    ) > 0
