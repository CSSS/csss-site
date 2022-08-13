import logging
import re

from elections.views.validators.validate_link import validate_link_for_nominee_social_media

logger = logging.getLogger('csss_site')


def validate_nominee_obj_info(nominee_names_so_far, full_name, facebook_link, linkedin_link, email_address,
                              discord_username):
    """
    validates the nominee info to validate it

    Keyword Arguments
    name -- the full name of the nominee
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
        f"[elections/validate_info_for_nominee_obj.py validate_nominee_obj_info()] "
        f"name={full_name}, facebook_link={facebook_link}, linkedin_link={linkedin_link}, email_address={email_address}, "
        f"discord_username={discord_username}"
    )
    full_name = full_name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    if full_name in nominee_names_so_far:
        return False, f"the nominee {full_name} has been specified more than once"
    nominee_names_so_far.append(full_name)
    if len(full_name) == 0 or full_name == "NONE":
        return False, "No valid name detected for one of the nominees"
    if len(facebook_link) == 0:
        return False, f"No valid facebook link detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no facebook link"
    success, error_message = validate_link_for_nominee_social_media(facebook_link, "Facebook", full_name)
    if not success:
        return False, error_message
    if len(linkedin_link) == 0:
        return False, f"No valid linkedin link detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no linkedin link"
    success, error_message = validate_link_for_nominee_social_media(linkedin_link, "LinkedIn", full_name)
    if not success:
        return False, error_message
    if len(email_address) == 0:
        return False, f"No valid email detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no email"
    regex = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w+$'
    if not (re.search(regex, email_address) or email_address == "NONE"):
        return False, f"email {email_address} for nominee {full_name} did not pass validation"
    if len(discord_username) == 0:
        return False, f"No valid discord username detected for nominee" \
                      f" {full_name}, please set to \"NONE\" if there is no discord " \
                      f"username "
    return True, None
