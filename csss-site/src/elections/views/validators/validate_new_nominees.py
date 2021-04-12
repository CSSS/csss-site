import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import NOM_POSITIONS_KEY, NOM_SPEECH_KEY
from elections.views.validators.validate_info_for_nominee_obj import validate_nominee_obj_info

logger = logging.getLogger('csss_site')


def validate_new_nominee(name, position_names_and_speeches, facebook_link, linkedin_link,
                         email_address, discord_username):
    """
    validates the nominee info to validate it

    Keyword Arguments
    name -- the full name of the nominee
    position_names_and_speeches -- a list of the pairings of the nominee's speeches and position_names
    facebook_link -- the link to the nominee's facebook profile
    linkedin_link -- the link to the nominee's linkedin page
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username

    Return
    Boolean -- indicates whether or not nominee information is valid which happens when any of the
    specified fields are empty
    error_message -- the error message if the nominees had an invalid input
    """
    validate_nominee_obj_info(name, facebook_link, linkedin_link, email_address, discord_username)
    specified_position_names = []
    for position_names_and_speech_pairing in position_names_and_speeches:
        if not (NOM_POSITIONS_KEY in position_names_and_speech_pairing and
                NOM_SPEECH_KEY in position_names_and_speech_pairing):
            return False, f"It seems that one of speech/position pairings for nominee" \
                          f" {name} has a missing position name or position speech"
        if not there_are_multiple_entries(position_names_and_speech_pairing, NOM_POSITIONS_KEY):
            return False, f"It seems that the nominee {name}" \
                          f" does not have a list of positions they are running for"
        for position_name in position_names_and_speech_pairing[NOM_POSITIONS_KEY]:
            if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name)) == 0:
                return False, f"Detected invalid position of {position_name} for nominee {name}"
            if position_name in specified_position_names:
                return False, f"the nominee {name} has the position {position_name} specified more than once"
            specified_position_names.append(position_name)
        if not (len(position_names_and_speech_pairing[NOM_SPEECH_KEY]) > 0):
            return False, f"No valid speech detected for nominee" \
                          f" {name}, please set to \"NONE\" if there is no speech"

    return True, None
