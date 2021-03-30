import logging

from elections.views.validators.json.validate_speech_and_position_names import speech_in_pairing, position_in_pairing

logger = logging.getLogger('csss_site')


def validate_existing_nominee(full_name, position_names_and_speech_pairing, facebook_link, linkedin_link,
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
    election_id -- the ID for the election that the nominee is running under

    Return
    Boolean -- indicates whether or not nominee information is valid which happens when any of the
    specified fields are empty
    error_message -- the error message if the nominees had an invalid input
    """
    logger.info(
        f"[elections/validate_nominee_new_json.py validate_existing_nominee()] "
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
