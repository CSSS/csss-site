from csss.views_helper import there_are_multiple_entries
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_INSTAGRAM
from elections.views.validators.validate_new_nominees import validate_new_nominee


def validate_new_nominees_for_new_election(nominees):
    """
    takes in a list of nominees to validate

    Keyword Arguments
    nominees -- a dictionary that contains a list of all the nominees to save under specified election

    Return
    Boolean -- true if election was saved and false if it was not
    error_message -- populated if the nominee[s] could not be saved
    """
    nominee_names_so_far = []
    for nominee in nominees:
        if not all_relevant_nominee_keys_exist(nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {ELECTION_JSON_KEY__NOM_NAME}, {ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS}, " \
                          f"{ELECTION_JSON_KEY__NOM_FACEBOOK},  {ELECTION_JSON_KEY__NOM_INSTAGRAM}, " \
                          f"{ELECTION_JSON_KEY__NOM_LINKEDIN}, {ELECTION_JSON_KEY__NOM_EMAIL}, " \
                          f"{ELECTION_JSON_KEY__NOM_DISCORD}"
        if not there_are_multiple_entries(nominee, ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS):
            return False, f"It seems that the nominee {nominee[ELECTION_JSON_KEY__NOM_NAME]} " \
                          f"does not have a list of speeches and positions they are running for"
        success, error_message = validate_new_nominee(nominee_names_so_far, nominee[ELECTION_JSON_KEY__NOM_NAME],
                                                      nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS],
                                                      nominee[ELECTION_JSON_KEY__NOM_FACEBOOK],
                                                      nominee[ELECTION_JSON_KEY__NOM_INSTAGRAM],
                                                      nominee[ELECTION_JSON_KEY__NOM_LINKEDIN],
                                                      nominee[ELECTION_JSON_KEY__NOM_EMAIL],
                                                      nominee[ELECTION_JSON_KEY__NOM_DISCORD])
        if not success:
            return False, error_message
    return True, None


def all_relevant_nominee_keys_exist(nominee):
    return ELECTION_JSON_KEY__NOM_NAME in nominee and ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee \
           and ELECTION_JSON_KEY__NOM_FACEBOOK in nominee and ELECTION_JSON_KEY__NOM_LINKEDIN in nominee \
           and ELECTION_JSON_KEY__NOM_EMAIL in nominee and ELECTION_JSON_KEY__NOM_DISCORD in nominee \
           and ELECTION_JSON_KEY__NOM_INSTAGRAM in nominee
