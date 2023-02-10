from elections.views.validators.validate_info_for_nominee_obj import validate_nominee_obj_info
from elections.views.validators.validate_speech_and_position_names import validate_speech_in_pairing, \
    validate_position_in_pairing


def validate_existing_nominee_jformat(nominee_names_so_far, speech_ids_so_far, position_ids_so_far, full_name,
                                      position_names_and_speech_pairings, facebook_link, instagram_link,
                                      linkedin_link, email_address, discord_id, election_id):
    """
    validates the nominee info to validate it

    Keyword Arguments
    name -- the full name of the nominee
    position_names_and_speech_pairings -- a list of the pairings of the nominee's speeches and position_names
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
    success, error_message = validate_nominee_obj_info(nominee_names_so_far, full_name, facebook_link, instagram_link,
                                                       linkedin_link,
                                                       email_address, discord_id)
    if not success:
        return success, error_message
    specified_position_names = []
    if not isinstance(position_names_and_speech_pairings, list):
        return False, f"It seems that the nominee {full_name} does not have a list of speeches" \
                      f" and positions they are running for"
    for position_names_and_speech_pairing in position_names_and_speech_pairings:
        success, error_message = validate_speech_in_pairing(speech_ids_so_far, position_names_and_speech_pairing,
                                                            election_id, full_name)
        if not success:
            return success, error_message
        success, error_message = validate_position_in_pairing(position_ids_so_far, position_names_and_speech_pairing,
                                                              specified_position_names, election_id, full_name)
        if not success:
            return success, error_message
    return True, None
