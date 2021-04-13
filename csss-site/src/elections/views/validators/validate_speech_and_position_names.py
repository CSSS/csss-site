from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries
from elections.models import NomineeSpeech, NomineePosition
from elections.views.Constants import NOM_SPEECH_KEY, NOM_ID_KEY, NOM_POSITIONS_KEY, \
    NOM_POSITION_KEY


def validate_speech_in_pairing(speech_and_position_pairing, election_id, name):
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
    if not (NOM_SPEECH_KEY in speech_and_position_pairing and
            len(speech_and_position_pairing[NOM_SPEECH_KEY]) > 0):
        return False, f"one of the speeches specified for {name} is invalid"
    if NOM_ID_KEY in speech_and_position_pairing:
        if valid_id_for_speech_pairing(speech_and_position_pairing, election_id):
            return True, None
        else:
            return False, f"one of the IDs specified for one of {name}'s speeches is invalid"
    else:
        return True, None


def valid_id_for_speech_pairing(speech_and_position_pairing, election_id):
    """
    returns a Bool that indicates if the ID in the speech_and_position_pairing is valid and belongs to a speech
     in the current election

    Keyword Argument
    speech_and_position_pairing -- the dict that contains the ID for the speech
    election_id -- the Id for the election to check if the speech belongs to it
    """
    return f"{speech_and_position_pairing[NOM_ID_KEY]}".isdigit() and \
           len(
               NomineeSpeech.objects.all().filter(
                   id=int(speech_and_position_pairing[NOM_ID_KEY]), nominee__election_id=election_id
               )
           ) == 1


def validate_position_in_pairing(speech_and_position_pairing, specified_position_names, election_id, name):
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
    if NOM_POSITIONS_KEY not in speech_and_position_pairing:
        return False, f"positions are not specified for one of the speeches for nominee {name}"
    if not there_are_multiple_entries(speech_and_position_pairing, NOM_POSITIONS_KEY):
        return False, f"It seems that the nominee {name} does not have a list of positions " \
                      f"for one of the positions they are running for"
    for position in speech_and_position_pairing[NOM_POSITIONS_KEY]:
        if type(position) is dict:
            if NOM_ID_KEY in position:
                if not valid_id_for_position_pairing(position, election_id):
                    return False, \
                           f"One of the IDs specified for one of the positions that {name} is running for is invalid"
            if not (NOM_POSITION_KEY in position):
                return False, f"No position name[s] found for one of the speeches for nominee {name}"
            position_name = position[NOM_POSITION_KEY]
        else:
            position_name = position
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name)) == 0:
            return False, f"Detected invalid position of {position_name} for nominee {name}"
        if position_name in specified_position_names:
            return False, f"the nominee {name} has the position {position_name} specified more than once"
        specified_position_names.append(position_name)
    return True, None


def valid_id_for_position_pairing(position_dict, election_id):
    """
    returns a Bool that indicates if the ID in the position_dict is valid and belongs to a position name
     in the current election

    Keyword Argument
    position_dict -- the dict that contains the ID for the position_name
    election_id -- the Id for the election to check if the position_name belongs to it
    """
    return (
            f"{position_dict[NOM_ID_KEY]}".isdigit() and
            len(
                NomineePosition.objects.all().filter(
                    id=int(position_dict[NOM_ID_KEY]), nominee_speech__nominee__election_id=election_id
                )
            ) == 0
    )
