from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries
from elections.models import NomineeSpeech, NomineePosition
from elections.views.election_management import NOM_SPEECH_POST_KEY, NOM_ID_POST_KEY, NOM_POSITIONS_POST_KEY, \
    NOM_POSITION_POST_KEY


def speech_in_pairing(speech_and_position_pairing, election_id, name):
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
    if not (NOM_SPEECH_POST_KEY in speech_and_position_pairing and
            len(speech_and_position_pairing[NOM_SPEECH_POST_KEY]) > 0):
        return False, f"one of the speeches specified for {name} is invalid"
    if NOM_ID_POST_KEY in speech_and_position_pairing:
        if f"{speech_and_position_pairing[NOM_ID_POST_KEY]}".isdigit() and \
                NomineeSpeech.objects.all().filter(id=int(speech_and_position_pairing[NOM_ID_POST_KEY]),
                                                   nominee__election_id=election_id):
            return True, None
        else:
            return False, f"one of the IDs specified for one of {name}'s speeches is invalid"
    else:
        return True, None


def position_in_pairing(speech_and_position_pairing, specified_position_names, election_id, name):
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
    if NOM_POSITIONS_POST_KEY not in speech_and_position_pairing:
        return False, f"positions are not specified for one of the speeches for nominee {name}"
    if not there_are_multiple_entries(speech_and_position_pairing, NOM_POSITIONS_POST_KEY):
        return False, f"It seems that the nominee {name} does not have a list of positions " \
                      f"for one of the positions they are running for"
    for position in speech_and_position_pairing[NOM_POSITIONS_POST_KEY]:
        if type(position) is dict:
            if NOM_ID_POST_KEY in position:
                if not (
                        f"{position[NOM_ID_POST_KEY]}".isdigit() and
                        NomineePosition.objects.all().filter(
                            id=int(position[NOM_ID_POST_KEY]), nominee_speech__nominee__election_id=election_id
                        )
                ):
                    return False, \
                           f"One of the IDs specified for one of the positions that {name} is running for is invalid"
            if not (NOM_POSITION_POST_KEY in position):
                return False, f"No position name[s] found for one of the speeches for nominee {name}"
            position_name = position[NOM_POSITION_POST_KEY]
        else:
            position_name = position
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name)) == 0:
            return False, f"Detected invalid position of {position_name} for nominee {name}"
        if position_name in specified_position_names:
            return False, f"the nominee {name} has the position {position_name} specified more than once"
        specified_position_names.append(position_name)
    return True, None