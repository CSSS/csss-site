import re

from about.views.input_new_officers.enter_new_officer_info.utils.get_discord_username_and_nickname import \
    get_discord_username_and_nickname
from about.views.input_new_officers.specify_new_officers.validators.validate_sfu_id import validate_sfu_id
from csss.setup_logger import Loggers
from elections.views.Constants import NA_STRING
from elections.views.validators.validate_link import validate_link_for_nominee_social_media


def validate_nominee_obj_info(nominee_names_so_far, full_name, sfuid, facebook_link, instagram_link, linkedin_link,
                              email_address, discord_id):
    """
    validates the nominee info to validate it

    Keyword Arguments
    nominee_names_so_far -- the names of the nominees who have been validated so far
    full_name -- the full name of the nominee
    sfuid -- the nominee's SFU ID
    facebook_link -- the link to the nominee's facebook profile
    instagram_link -- the link to the nominee's Instagram profile
    linkedin_link -- the link to the nominee's linkedin page
    email_address -- the nominee's email address
    discord_id -- the nominee's discord ID

    Return
    Boolean -- indicates whether nominee information is valid which happens when any of the
    specified fields are empty
    error_message -- the error message if the nominees had an invalid input
    """
    logger = Loggers.get_logger()
    logger.info(
        f"[elections/validate_info_for_nominee_obj.py validate_nominee_obj_info()] "
        f"name={full_name}, facebook_link={facebook_link}, linkedin_link={linkedin_link}, "
        f"email_address={email_address}, discord_id={discord_id}"
    )
    full_name = full_name.strip()
    facebook_link = facebook_link.strip()
    instagram_link = instagram_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    if full_name in nominee_names_so_far:
        return False, f"the nominee {full_name} has been specified more than once"
    nominee_names_so_far.append(full_name)
    if len(full_name) == 0 or full_name == NA_STRING:
        return False, "No valid name detected for one of the nominees"
    success, error_message = validate_sfu_id(sfuid)
    if not success:
        return False, error_message
    if len(facebook_link) == 0:
        return False, f"No valid facebook link detected for nominee" \
                      f" {full_name}, please set to \"{NA_STRING}\" if there is no facebook link"
    success, error_message = validate_link_for_nominee_social_media(facebook_link, "Facebook", full_name)
    if not success:
        return False, error_message
    if len(instagram_link) == 0:
        return False, f"No valid instagram link detected for nominee" \
                      f" {full_name}, please set to \"{NA_STRING}\" if there is no instagram link"
    success, error_message = validate_link_for_nominee_social_media(instagram_link, "Instagram", full_name)
    if not success:
        return False, error_message
    if len(linkedin_link) == 0:
        return False, f"No valid linkedin link detected for nominee" \
                      f" {full_name}, please set to \"{NA_STRING}\" if there is no linkedin link"
    success, error_message = validate_link_for_nominee_social_media(linkedin_link, "LinkedIn", full_name)
    if not success:
        return False, error_message
    if len(email_address) == 0:
        return False, f"No valid email detected for nominee" \
                      f" {full_name}, please set to \"{NA_STRING}\" if there is no email"
    regex = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w+$'
    if not (re.search(regex, email_address) or email_address == NA_STRING):
        return False, f"email {email_address} for nominee {full_name} did not pass validation"
    if discord_id != NA_STRING:
        success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(discord_id)
        if not success:
            return False, error_message
    return True, None
