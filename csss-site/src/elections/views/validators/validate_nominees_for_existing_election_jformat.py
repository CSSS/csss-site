from elections.models import Nominee
from elections.views.Constants import ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ID_KEY
from elections.views.validators.validate_existing_nominee_jformat import validate_existing_nominee_jformat


def validate_nominees_for_existing_election_jformat(election_id, nominees):
    """
    takes in a list of nominees to validate

    Keyword Arguments
    election_id -- the ID for the election that the user is running under
    nominees -- a dictionary that contains a list of all the nominees to save under specified election

    Return
    Boolean -- true if election was saved and false if it was not
    error_message -- populated if the nominee[s] could not be saved
    """
    nominee_names_so_far = []
    for nominee in nominees:
        if not (ELECTION_JSON_KEY__NOM_NAME in nominee and ELECTION_JSON_KEY__NOM_FACEBOOK in nominee
                and ELECTION_JSON_KEY__NOM_LINKEDIN in nominee and ELECTION_JSON_KEY__NOM_EMAIL in nominee
                and ELECTION_JSON_KEY__NOM_DISCORD in nominee
                and ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {ELECTION_JSON_KEY__NOM_NAME}, {ELECTION_JSON_KEY__NOM_FACEBOOK}, " \
                          f"{ELECTION_JSON_KEY__NOM_LINKEDIN}, " \
                          f"{ELECTION_JSON_KEY__NOM_EMAIL}, {ELECTION_JSON_KEY__NOM_DISCORD}, " \
                          f"{ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS}"
        if ID_KEY in nominee:
            if f"{nominee[ID_KEY]}".isdigit():
                matching_nominees_under_specified_election = Nominee.objects.all().filter(
                    id=int(nominee[ID_KEY]),
                    election_id=election_id
                )
                if len(matching_nominees_under_specified_election) == 0:
                    return False, f"Invalid nominee id of {int(nominee[ID_KEY])} detected"
            else:
                return False, f"Invalid type detected for nominee id of {nominee[ID_KEY]}"

        success, error_message = validate_existing_nominee_jformat(
            nominee_names_so_far,
            nominee[ELECTION_JSON_KEY__NOM_NAME],
            nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS],
            nominee[ELECTION_JSON_KEY__NOM_FACEBOOK],
            nominee[ELECTION_JSON_KEY__NOM_LINKEDIN],
            nominee[ELECTION_JSON_KEY__NOM_EMAIL],
            nominee[ELECTION_JSON_KEY__NOM_DISCORD], election_id
        )
        if not success:
            return False, error_message
    return True, None
