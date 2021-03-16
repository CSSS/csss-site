import logging

from csss.views_helper import there_are_multiple_entries
from elections.views.election_management import NOM_NAME_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, \
    NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, NOM_POSITION_AND_SPEECH_POST_KEY
from elections.views.validators.validate_nominee_new import validate_new_nominee

logger = logging.getLogger('csss_site')


def validate_new_nominees_for_new_election_from_json(nominees):
    """
    takes in a list of nominees to validate

    Keyword Arguments
    nominees -- a dictionary that contains a list of all the nominees to save under specified election

    Return
    Boolean -- true if election was saved and false if it was not
    error_message -- populated if the nominee[s] could not be saved
    """
    for nominee in nominees:
        if not (NOM_NAME_POST_KEY in nominee and NOM_FACEBOOK_POST_KEY in nominee
                and NOM_LINKEDIN_POST_KEY in nominee and NOM_EMAIL_POST_KEY in nominee
                and NOM_DISCORD_USERNAME_POST_KEY in nominee and NOM_POSITION_AND_SPEECH_POST_KEY in nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {NOM_NAME_POST_KEY}, {NOM_FACEBOOK_POST_KEY}, {NOM_LINKEDIN_POST_KEY}, " \
                          f" {NOM_EMAIL_POST_KEY}, {NOM_DISCORD_USERNAME_POST_KEY}," \
                          f" {NOM_POSITION_AND_SPEECH_POST_KEY}"
        if not there_are_multiple_entries(nominee, NOM_POSITION_AND_SPEECH_POST_KEY):
            return False, f"It seems that the nominee {nominee[NOM_NAME_POST_KEY]} does not have a list of speeches" \
                          f" and positions they are running for"
        success, error_message = validate_new_nominee(
            nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_AND_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY], nominee[NOM_DISCORD_USERNAME_POST_KEY]
        )
        if not success:
            return False, error_message
    return True, None

