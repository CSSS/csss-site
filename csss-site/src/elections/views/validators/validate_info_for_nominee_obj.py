import logging

from elections.views.validators.validate_link import validate_http_link

logger = logging.getLogger('csss_site')


def validate_nominee_obj_info(nominee_names_so_far, name, facebook_link, linkedin_link, email_address,
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
        f"name={name}, facebook_link={facebook_link}, linkedin_link={linkedin_link}, email_address={email_address}, "
        f"discord_username={discord_username}"
    )
    name = name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    if name in nominee_names_so_far:
        return False, f"the nominee {name} has been specified more than once"
    nominee_names_so_far.append(name)
    if len(name) == 0 or name == "NONE":
        return False, "No valid name detected for one of the nominees"
    if len(facebook_link) == 0:
        return False, f"No valid facebook link detected for nominee" \
                      f" {name}, please set to \"NONE\" if there is no facebook link"
    success, error_message = validate_http_link(facebook_link, "facebook", nom_name=name)
    if not success:
        return False, error_message
    if len(linkedin_link) == 0:
        return False, f"No valid linkedin link detected for nominee" \
                      f" {name}, please set to \"NONE\" if there is no linkedin link"
    success, error_message = validate_http_link(linkedin_link, "linkedin", nom_name=name)
    if not success:
        return False, error_message
    if len(email_address) == 0:
        return False, f"No valid email detected for nominee" \
                      f" {name}, please set to \"NONE\" if there is no email"
    if len(discord_username) == 0:
        return False, f"No valid discord username detected for nominee" \
                      f" {name}, please set to \"NONE\" if there is no discord " \
                      f"username "
    return True, None
