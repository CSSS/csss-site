from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import ELECTION_NOMINEES_KEY, \
    NOM_POSITION_AND_SPEECH_KEY, NOM_POSITIONS_KEY, NOM_SPEECH_KEY, \
    NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, NOM_EMAIL_KEY, NOM_DISCORD_USERNAME_KEY, NOM_ID_KEY, \
    ELECTION_DATE_KEY, ELECTION_TIME_KEY, ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_ID_KEY, \
    NOM_NAME_KEY


def create_webform_context():
    """
    Creating context for WebForm pages for election creation or modification

    returns a dict with the following keys
    positions
    time_key
    election_type_key
    websurvey_link_key
    nominee_key
    speech_and_position_pairing_key
    position_names_key
    speech_key
    speech_id
    name_key
    facebook_key
    linkedin_key
    email_key
    discord_key
    nominee_id_key
    election_types
    election_id_key
    """
    return {
        'positions': OfficerEmailListAndPositionMapping.objects.all().order_by('position_index'),
        'date_key': ELECTION_DATE_KEY,
        'time_key': ELECTION_TIME_KEY,
        'election_type_key': ELECTION_TYPE_KEY,
        'websurvey_link_key': ELECTION_WEBSURVEY_LINK_KEY,
        'nominee_key': ELECTION_NOMINEES_KEY,
        'speech_and_position_pairing_key': NOM_POSITION_AND_SPEECH_KEY,
        'position_names_key': NOM_POSITIONS_KEY,
        'speech_key': NOM_SPEECH_KEY,
        'speech_id': NOM_ID_KEY,
        'name_key': NOM_NAME_KEY,
        'facebook_key': NOM_FACEBOOK_KEY,
        'linkedin_key': NOM_LINKEDIN_KEY,
        'email_key': NOM_EMAIL_KEY,
        'discord_key': NOM_DISCORD_USERNAME_KEY,
        'nominee_id_key': NOM_ID_KEY,
        'election_types': Election.election_type_choices,
        'election_id_key': ELECTION_ID_KEY
    }


def create_webform_context_with_pre_populated_election_data(error_message, election_dict=None):
    """
    Returns a dict that is populated with the error message as the sole entry under the key 'error_messages'
    along with the election data under the following keys
    date
    time
    selected_election_type
    websurvey
    nominees
    """
    context = {ERROR_MESSAGES_KEY: [error_message]}
    if election_dict is not None:
        if ELECTION_DATE_KEY in election_dict:
            context[ELECTION_DATE_KEY] = election_dict[ELECTION_DATE_KEY]
        if ELECTION_TIME_KEY in election_dict:
            context[ELECTION_TIME_KEY] = election_dict[ELECTION_TIME_KEY]
        if ELECTION_TYPE_KEY in election_dict:
            context[ELECTION_TYPE_KEY] = election_dict[ELECTION_TYPE_KEY]
        if ELECTION_WEBSURVEY_LINK_KEY in election_dict:
            context[ELECTION_WEBSURVEY_LINK_KEY] = election_dict[ELECTION_WEBSURVEY_LINK_KEY]
        if ELECTION_NOMINEES_KEY in election_dict:
            context[ELECTION_NOMINEES_KEY] = election_dict[ELECTION_NOMINEES_KEY]
    return context
