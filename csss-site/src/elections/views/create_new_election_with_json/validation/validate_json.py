import json
import logging
import datetime

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election
from elections.views.election_management import JSON_INPUT_FIELD_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_DATE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY, NOM_NAME_POST_KEY, \
    NOM_POSITION_POST_KEY, NOM_SPEECH_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, NOM_EMAIL_POST_KEY, \
    NOM_DISCORD_USERNAME_POST_KEY

logger = logging.getLogger('csss_site')


def validate_inputted_election_json(request):
    if JSON_INPUT_FIELD_POST_KEY not in request.POST:
        error_message = "Could not find the json in the input"
        logger.info("[elections/election_management.py process_new_election_information_from_json()] "
                    f"{error_message}")
        return False, [error_message], None
    try:
        election_json = json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY])
    except json.decoder.JSONDecodeError as e:
        error_messages = f"Unable to decode the input due to error: {e}"
        logger.info(
            "[elections/election_management.py process_new_election_information_from_json()] "
            f"{error_messages}"
        )
        return False, [error_messages], json.dumps(
            request.POST[JSON_INPUT_FIELD_POST_KEY]
        ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")

    if not (ELECTION_TYPE_POST_KEY in election_json and
            ELECTION_DATE_POST_KEY in election_json and
            ELECTION_WEBSURVEY_LINK_POST_KEY in election_json and
            ELECTION_NOMINEES_POST_KEY in election_json):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_TYPE_POST_KEY}, {ELECTION_DATE_POST_KEY}, {ELECTION_WEBSURVEY_LINK_POST_KEY}, " \
                        f"{ELECTION_NOMINEES_POST_KEY}"
        logger.info(
            f"[elections/election_management.py process_new_election_information_from_json()] {error_message}"
        )
        return False, [error_message], election_json

    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    election_type = election_json[ELECTION_TYPE_POST_KEY]
    if election_type not in valid_election_type_choices:
        error_message = f"election_type of {election_type} " \
                        f"is not one of the valid options: {valid_election_type_choices}"
        logger.error(
            "[elections/election_management.py _validate_and_return_information_from_new_election()]"
            f" {error_message}"
        )
        return False, [error_message], election_json

    try:
        datetime.datetime.strptime(f"{election_json[ELECTION_DATE_POST_KEY]}", '%Y-%m-%d %H:%M')
    except ValueError:
        error_message = f" given date of {election_json[ELECTION_DATE_POST_KEY]} is not in the" \
                        f" valid format of YYYY-MM-DD HH:MM"
        logger.error(
            "[elections/election_management.py _validate_and_return_information_for_new_election_from_json()]"
            f"{error_message}"
        )
        return False, [error_message], election_json
    except TypeError:
        error_message = "given date seems to be unreadable"
        logger.error(
            f"[elections/election_management.py _validate_and_return_information_for_new_election_from_json()]"
            f" {error_message}"
        )
        return False, [error_message], election_json
    nominees = election_json[ELECTION_NOMINEES_POST_KEY]
    success, error_message = _validate_new_nominees_for_new_election_from_json(nominees)
    if not success:
        return False, [error_message], election_json
    return True, None, None


def _validate_new_nominees_for_new_election_from_json(nominees):
    """takes in a list of nominees to save under the given nomination page from the json page

    Keyword Arguments
    nominees -- a dictionary that contains a list of all the nominees to save under specified election

    Return
    Boolean -- true if election was saved and false if it was not
    error_message -- populated if the nominee[s] could not be saved
    """
    for nominee in nominees:
        if not(NOM_NAME_POST_KEY in nominee and NOM_POSITION_POST_KEY in nominee
               and NOM_SPEECH_POST_KEY in nominee and NOM_FACEBOOK_POST_KEY in nominee
               and NOM_LINKEDIN_POST_KEY in nominee and NOM_EMAIL_POST_KEY in nominee
               and NOM_DISCORD_USERNAME_POST_KEY in nominee):
            return False, f"It seems that one of the nominees is missing one of the following fields:" \
                          f" {NOM_NAME_POST_KEY}, {NOM_POSITION_POST_KEY}, {NOM_SPEECH_POST_KEY}," \
                          f" {NOM_FACEBOOK_POST_KEY}, {NOM_LINKEDIN_POST_KEY}, {NOM_EMAIL_POST_KEY}," \
                          f" {NOM_DISCORD_USERNAME_POST_KEY}"
        success, error_message = _validate_new_nominee(
            nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_POST_KEY],
            nominee[NOM_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
            nominee[NOM_DISCORD_USERNAME_POST_KEY]
        )
        if not success:
            return False, error_message
    return True, None


def _validate_new_nominee(full_name, position_names, speech, facebook_link, linkedin_link,
                          email_address, discord_username):
    """Takes in the info of a single nominee [except its election] and creates the nominee object
    that will need to be saved

    Keyword Arguments
    full_name -- the full name of the nominee
    position_names -- the officer positions the nominee is running for
    speech -- the nominee's speech for the position
    facebook_link -- the link to the nominee's facebook profile
    linkedin_link -- the link to the nominee's linkedin page
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username
    nominee_index -- the index of the nominee which determines in what order the nominee will be shown on
    the nomination page

    Return
    Boolean -- indicates whether or not nominee information is valid which happens when any of the
    specified fields are empty
    error_message -- the error message if the nominee could not be created
    """

    if len(full_name.strip()) == 0 or full_name.strip().upper() == "NONE":
        return False, "No valid name detected for one of the nominees"
    if len(position_names) == 0 or not isinstance(position_names, list):
        return False, f"No valid position detected for nominee {full_name}"
    for position_name in position_names:
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name)) == 0:
            return False, f"Position {position_name} detected for nominee {full_name} is not valid"
    if len(speech) == 0:
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
