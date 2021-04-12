from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import NOM_NAME_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, \
    NOM_EMAIL_KEY, NOM_DISCORD_USERNAME_KEY, NOM_POSITION_AND_SPEECH_KEY
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
    for nominee in nominees:
        if not (NOM_NAME_KEY in nominee and NOM_FACEBOOK_KEY in nominee
                and NOM_LINKEDIN_KEY in nominee and NOM_EMAIL_KEY in nominee
                and NOM_DISCORD_USERNAME_KEY in nominee and NOM_POSITION_AND_SPEECH_KEY in nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {NOM_NAME_KEY}, {NOM_FACEBOOK_KEY}, {NOM_LINKEDIN_KEY}, " \
                          f" {NOM_EMAIL_KEY}, {NOM_DISCORD_USERNAME_KEY}," \
                          f" {NOM_POSITION_AND_SPEECH_KEY}"
        if not there_are_multiple_entries(nominee, NOM_POSITION_AND_SPEECH_KEY):
            return False, f"It seems that the nominee {nominee[NOM_NAME_KEY]} does not have a list of speeches" \
                          f" and positions they are running for"
        success, error_message = validate_new_nominee(
            nominee[NOM_NAME_KEY], nominee[NOM_POSITION_AND_SPEECH_KEY], nominee[NOM_FACEBOOK_KEY],
            nominee[NOM_LINKEDIN_KEY], nominee[NOM_EMAIL_KEY], nominee[NOM_DISCORD_USERNAME_KEY]
        )
        if not success:
            return False, error_message
    return True, None
