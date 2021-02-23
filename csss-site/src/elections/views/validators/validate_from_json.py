import datetime
import json
import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries
from elections.models import Election
from elections.views.election_management import NOM_NAME_POST_KEY, \
    NOM_POSITION_POST_KEY, NOM_SPEECH_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, NOM_EMAIL_POST_KEY, \
    NOM_DISCORD_USERNAME_POST_KEY, NOM_POSITION_AND_SPEECH_POST_KEY

logger = logging.getLogger('csss_site')


def validate_and_return_election_json(input_json):
    try:
        election_json = json.loads(input_json)
        return True, None, election_json
    except json.decoder.JSONDecodeError as e:
        error_messages = f"Unable to decode the input due to error: {e}"
        logger.info(
            "[elections/validate_from_json.py validate_inputted_election_json()] "
            f"{error_messages}"
        )
        return False, [error_messages], \
            json.dumps(
                input_json
            ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")


def validate_election_type(election_type):
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    if election_type not in valid_election_type_choices:
        error_message = f"election_type of {election_type} is not one of the valid options."
        logger.error(
            "[elections/validate_from_json.py validate_inputted_election_json()]"
            f" {error_message}"
        )
        return False, error_message
    return True, None


def validate_election_date(date):
    try:
        datetime.datetime.strptime(f"{date}", '%Y-%m-%d %H:%M')
    except ValueError:
        error_message = f" given date of {date} is not in the valid format"
        logger.error(
            "[elections/validate_from_json.py validate_inputted_election_json()]"
            f"{error_message}"
        )
        return False, error_message
    except TypeError as e:
        error_message = "given date seems to be unreadable"
        logger.error(
            f"[elections/validate_from_json.py validate_inputted_election_json()]"
            f" {error_message} due to following error \n{e}"
        )
        return False, error_message
    return True, None


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
        if not (NOM_NAME_POST_KEY in nominee and NOM_POSITION_POST_KEY in nominee
                and NOM_SPEECH_POST_KEY in nominee and NOM_FACEBOOK_POST_KEY in nominee
                and NOM_LINKEDIN_POST_KEY in nominee and NOM_EMAIL_POST_KEY in nominee
                and NOM_DISCORD_USERNAME_POST_KEY in nominee and NOM_POSITION_AND_SPEECH_POST_KEY in nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {NOM_NAME_POST_KEY}, {NOM_POSITION_POST_KEY}, {NOM_SPEECH_POST_KEY}," \
                          f" {NOM_FACEBOOK_POST_KEY}, {NOM_LINKEDIN_POST_KEY}, {NOM_EMAIL_POST_KEY}," \
                          f" {NOM_DISCORD_USERNAME_POST_KEY}"
        if not there_are_multiple_entries(nominee, NOM_POSITION_AND_SPEECH_POST_KEY):
            return False, f"It seems that the nominee {nominee[NOM_NAME_POST_KEY]} does not have a list of speeches" \
                          f" and positions they are running for"
        for position in nominee[NOM_POSITION_AND_SPEECH_POST_KEY]:
            if not (NOM_POSITION_POST_KEY in position and NOM_SPEECH_POST_KEY in position):
                return False, f"It seems that one of speech/position pairings for nominee" \
                              f" {nominee[NOM_NAME_POST_KEY]} has a missing position name or position speech"
            if not there_are_multiple_entries(position, NOM_POSITION_POST_KEY):
                return False, f"It seems that the nominee {nominee[NOM_NAME_POST_KEY]}" \
                              f" does not have a list of positions they are running for"
        success, error_message = _validate_new_nominee(
            nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_AND_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY], nominee[NOM_DISCORD_USERNAME_POST_KEY]
        )
        if not success:
            return False, error_message
    return True, None


def _validate_nominee_for_existing_election_from_json(nominees):
    for nominee in nominees:
        if not (NOM_NAME_POST_KEY in nominee and NOM_POSITION_POST_KEY in nominee
                and NOM_SPEECH_POST_KEY in nominee and NOM_FACEBOOK_POST_KEY in nominee
                and NOM_LINKEDIN_POST_KEY in nominee and NOM_EMAIL_POST_KEY in nominee
                and NOM_DISCORD_USERNAME_POST_KEY in nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {NOM_NAME_POST_KEY}, {NOM_POSITION_POST_KEY}, {NOM_SPEECH_POST_KEY}," \
                          f" {NOM_FACEBOOK_POST_KEY}, {NOM_LINKEDIN_POST_KEY}, {NOM_EMAIL_POST_KEY}," \
                          f" {NOM_DISCORD_USERNAME_POST_KEY}"
        success, error_message = _validate_new_nominee(
            nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_AND_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY], nominee[NOM_DISCORD_USERNAME_POST_KEY]
        )
        if not success:
            return False, error_message
    return True, None


def _validate_new_nominee(full_name, position_names_and_speeches, facebook_link, linkedin_link,
                          email_address, discord_username):
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
        f"full_name={full_name}, position_names_and_speeches={position_names_and_speeches}, facebook_link={facebook_link}, "
        f"linkedin_link={linkedin_link}, email_address={email_address}, discord_username={discord_username}"
    )
    full_name = full_name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    specified_position_names = []
    for position_names_and_speech_pairing in position_names_and_speeches:
        if len(full_name) == 0 or full_name.upper() == "NONE":
            return False, "No valid name detected for one of the nominees"
        for position_name in position_names_and_speech_pairing[NOM_POSITION_POST_KEY]:
            if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name)) == 0:
                return False, f"Detected invalid position of {position_name} for nominee {full_name}"
            if position_name in specified_position_names:
                return False, f"the nominee {full_name} has the position {position_name} specified more than once"
            specified_position_names.append(position_name)
        if len(position_names_and_speech_pairing[NOM_SPEECH_POST_KEY]) == 0:
            return False, f"No valid speech detected for nominee" \
                          f" {full_name}, please set to \"NONE\" if there is no speech"
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
    return True, None
