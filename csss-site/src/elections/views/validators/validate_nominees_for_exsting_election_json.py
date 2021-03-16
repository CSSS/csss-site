from elections.models import Nominee
from elections.views.election_management import NOM_NAME_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, \
    NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, NOM_POSITION_AND_SPEECH_POST_KEY, NOM_ID_POST_KEY
from elections.views.validators.validate_nominee_new_json import validate_existing_nominee


def validate_nominees_for_existing_election_from_json(election_id, nominees):
    """
    takes in a list of nominees to validate

    Keyword Arguments
    election_id -- the ID for the election that the user is running under
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

        success, error_message = validate_existing_nominee(
            nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_AND_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY], nominee[NOM_DISCORD_USERNAME_POST_KEY],
            election_id
        )
        if not success:
            return False, error_message
    return True, None
