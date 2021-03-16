import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.election_management import NOM_NAME_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, \
    NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, NOM_POSITION_AND_SPEECH_POST_KEY, NOM_ID_POST_KEY, \
    NOM_SPEECH_POST_KEY, NOM_POSITIONS_POST_KEY, NOM_POSITION_POST_KEY

logger = logging.getLogger('csss_site')


def validate_nominees_for_existing_election_from_json(election_id, nominees):
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
                          f"{NOM_EMAIL_POST_KEY}, {NOM_DISCORD_USERNAME_POST_KEY}, " \
                          f"{NOM_POSITION_AND_SPEECH_POST_KEY}"
        if NOM_ID_POST_KEY in nominee:
            if f"{nominee[NOM_ID_POST_KEY]}".isdigit():
                matching_nominees_under_specified_election = Nominee.objects.all().filter(
                    id=int(nominee[NOM_ID_POST_KEY]),
                    election_id=election_id
                )
                if len(matching_nominees_under_specified_election) == 0:
                    return False, f"Invalid nominee id of {int(nominee[NOM_ID_POST_KEY])} detected"
            else:
                return False, f"Invalid type detected for nominee id of {int(nominee[NOM_ID_POST_KEY])}"

        success, error_message = _validate_existing_nominee(
            nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_AND_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY], nominee[NOM_DISCORD_USERNAME_POST_KEY],
            election_id
        )
        if not success:
            return False, error_message
    return True, None


def _validate_existing_nominee(full_name, position_names_and_speech_pairing, facebook_link, linkedin_link,
                               email_address, discord_username, election_id):
    """
    validates the nominee info to validate it

    Keyword Arguments
    full_name -- the full name of the nominee
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
    logger.info(
        f"[elections/validate_from_json.py _validate_new_nominee()] "
        f"full_name={full_name}, position_names_and_speeches={position_names_and_speech_pairing}, "
        f"facebook_link={facebook_link}, linkedin_link={linkedin_link}, email_address={email_address}, "
        f"discord_username={discord_username}"
    )
    full_name = full_name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    if len(full_name) == 0 or full_name.upper() == "NONE":
        return False, "No valid name detected for one of the nominees"
    if len(facebook_link) == 0:
        return False, f"No valid facebook link detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no facebook link"
    if len(linkedin_link) == 0:
        return False, f"No valid linkedin link detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no linkedin link"
    if len(email_address) == 0:
        return False, f"No valid email detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no email"
    if len(discord_username) == 0:
        return False, f"No valid discord username detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no discord " \
                      f"username "
    specified_position_names = []
    if not isinstance(position_names_and_speech_pairing, list):
        return False, f"It seems that the nominee {full_name} does not have a list of speeches" \
                      f" and positions they are running for"
    for position_names_and_speech_pairing in position_names_and_speech_pairing:
        success, error_message = speech_in_pairing(
            position_names_and_speech_pairing, election_id, full_name
        )
        if not success:
            return success, error_message
        success, error_message = position_in_pairing(
            position_names_and_speech_pairing, specified_position_names, election_id, full_name
        )
        if not success:
            return success, error_message
    return True, None


def speech_in_pairing(speech_and_position_pairing, election_id, name):
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