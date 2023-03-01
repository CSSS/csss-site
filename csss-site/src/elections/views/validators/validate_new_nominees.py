from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import NA_STRING
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH
from elections.views.validators.validate_info_for_nominee_obj import validate_nominee_obj_info


def validate_new_nominee(nominee_names_so_far, full_name, sfuid, position_names_and_speech_pairings, facebook_link,
                         instagram_link, linkedin_link, email_address, discord_id):
    """
    validates the nominee info to validate it

    Keyword Arguments
    nominee_names_so_far -- the names of the nominees who have been validated so far
    full_name -- the full name of the nominee
    sfuid -- the nominee's SFU ID
    position_names_and_speech_pairing -- a list of the pairings of the nominee's speeches and position_names
    facebook_link -- the link to the nominee's facebook profile
    instagram_link -- the link to the nominee's instagram page
    linkedin_link -- the link to the nominee's linkedin page
    email_address -- the nominee's email address
    discord_id -- the nominee's discord ID

    Return
    Boolean -- indicates whether nominee information is valid which happens when any of the
    specified fields are empty
    error_message -- the error message if the nominees had an invalid input
    """
    success, error_message = validate_nominee_obj_info(nominee_names_so_far, full_name, sfuid, facebook_link,
                                                       instagram_link, linkedin_link, email_address, discord_id)
    if not success:
        return success, error_message
    specified_position_names = []
    for position_names_and_speech_pairing in position_names_and_speech_pairings:
        if not all_relevant_position_names_and_speech_pairing_keys_exist(position_names_and_speech_pairing):
            return False, f"It seems that one of speech/position pairings for nominee" \
                          f" {full_name} has a missing position name or position speech"
        if not there_are_multiple_entries(position_names_and_speech_pairing, ELECTION_JSON_KEY__NOM_POSITION_NAMES):
            return False, f"It seems that the nominee {full_name}" \
                          f" does not have a list of positions they are running for"
        for position_name in position_names_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]:
            if not validate_position_name(position_name):
                return False, f"Detected invalid position of {position_name} for nominee {full_name}"
            if position_name in specified_position_names:
                return False, f"the nominee {full_name} has the position {position_name} specified more than once"
            specified_position_names.append(position_name)
        if not (len(position_names_and_speech_pairing[ELECTION_JSON_KEY__NOM_SPEECH]) > 0):
            return False, f"No valid speech detected for nominee" \
                          f" {full_name}, please set to \"{NA_STRING}\" if there is no speech"

    return True, None


def all_relevant_position_names_and_speech_pairing_keys_exist(position_names_and_speech_pairings):
    return ELECTION_JSON_KEY__NOM_POSITION_NAMES in position_names_and_speech_pairings \
           and ELECTION_JSON_KEY__NOM_SPEECH in position_names_and_speech_pairings


def validate_position_name(position_name):
    """
    returns a Bool that indicates if the position name is for a CSSS position that is elected via an election officer

    Keyword Argument
    position_name -- the name of the position
    """
    return len(
        OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=position_name, marked_for_deletion=False, elected_via_election_officer=True
        )
    ) > 0
