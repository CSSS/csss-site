import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import ERROR_MESSAGES_KEY
from elections.models import Election

from elections.views.Constants import INPUT_ELECTION_ID__NAME, INPUT_ELECTION_ID__VALUE, INPUT_DATE__NAME, \
    INPUT_DATE__VALUE, INPUT_TIME__NAME, INPUT_TIME__VALUE, SELECT_ELECTION_TYPE__NAME, \
    SELECTED_ELECTION_TYPE__HTML_NAME, CREATE_NEW_ELECTION__HTML_NAME, NOMINEES_HTML__NAME, CURRENT_WEBSURVEY_LINK, \
    NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH__NAME, INPUT_NOMINEE_FACEBOOK__NAME, \
    INPUT_NOMINEE_LINKEDIN__NAME, INPUT_NOMINEE_EMAIL__NAME, INPUT_NOMINEE_DISCORD__NAME, \
    INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, INPUT_NOMINEE_POSITION_NAMES__NAME, CURRENT_ELECTION_TYPES, \
    ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_WEBFORM_KEY__TIME, INPUT_WEBSURVEY__NAME, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_SPEECH, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, \
    ELECTION_JSON_KEY__NOM_DISCORD, INPUT_NOMINEE_NAME__NAME, ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    CURRENT_OFFICER_POSITIONS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_ID, ELECTION_JSON_KEY__ELECTION_TYPE, \
    DATE_FORMAT, TIME_FORMAT, INPUT_NOMINEE_ID__NAME, ID_KEY, INPUT_SPEECH_ID__NAME
from elections.views.create_context.submission_buttons_context import create_submission_buttons_context
from elections.views.extractors.get_election_nominees import get_election_nominees
from elections.views.extractors.get_existing_election_by_id import get_existing_election_by_id

logger = logging.getLogger('csss_site')


def create_webform_context(create_new_election=True):
    """
    Creating context for WebForm pages for election creation or modification

    Keyword Argument
    create_new_election - bool that determines if context will have a value of True or False for
     create_new_election__html_name

    Return
    dict - with the following keys
    input_date__name
    input_time__name
    select_election_type__name
    election_types
    input_websurvey__name

    nominee_div__name

    input_nominee_id__name
    input_nominee_name__name
    input_nominee_facebook__name
    input_nominee_linkedin__name
    input_nominee_email__name
    input_nominee_discord__name

    current_officer_positions
    input_nominee_speech_and_position_pairing__name
    input_nominee_position_names__name
    input_nominee_speech__name
    input_speech_id__name

    create_new_election__html_name

    along with keys from create_submission_buttons_context(
    """
    context = {
        INPUT_DATE__NAME: ELECTION_JSON_KEY__DATE,
        INPUT_TIME__NAME: ELECTION_JSON_WEBFORM_KEY__TIME,
        SELECT_ELECTION_TYPE__NAME: ELECTION_JSON_KEY__ELECTION_TYPE,
        CURRENT_ELECTION_TYPES: Election.election_type_choices,
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,

        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEES,

        INPUT_NOMINEE_ID__NAME: ID_KEY,
        INPUT_NOMINEE_NAME__NAME: ELECTION_JSON_KEY__NOM_NAME,
        INPUT_NOMINEE_FACEBOOK__NAME: ELECTION_JSON_KEY__NOM_FACEBOOK,
        INPUT_NOMINEE_LINKEDIN__NAME: ELECTION_JSON_KEY__NOM_LINKEDIN,
        INPUT_NOMINEE_EMAIL__NAME: ELECTION_JSON_KEY__NOM_EMAIL,
        INPUT_NOMINEE_DISCORD__NAME: ELECTION_JSON_KEY__NOM_DISCORD,

        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_position=True
            )
        ],
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        INPUT_SPEECH_ID__NAME: ID_KEY,

        CREATE_NEW_ELECTION__HTML_NAME: create_new_election,

    }
    context.update(create_submission_buttons_context(create_new_election=create_new_election))
    logger.info("[elections/create_webform_context.py create_webform_context()] "
                f"created context of '{context}'")
    return context


def create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict=None):
    """
    Returns a dict that is populated with the error message as the sole entry under the key 'error_messages'
    along with the election data under the following keys

    Keyword Arguments
    error_message -- the error message to store in the context
    election_dict -- the dict that contains the election info that has to be transferred to the context

    Return
    a dict with the following keys
    error_messages
    input_election_id__name
    input_election_id__value
    input_date__value
    input_time__value
    selected_election_type__html_name
    current_websurvey_link
    nominees__html_name
    """
    context = {
        ERROR_MESSAGES_KEY: [error_message]
    }
    if election_dict is not None:
        if ELECTION_ID in election_dict:
            context[INPUT_ELECTION_ID__NAME] = ELECTION_ID
            context[INPUT_ELECTION_ID__VALUE] = election_dict[ELECTION_ID]
        if ELECTION_JSON_KEY__DATE in election_dict:
            context[INPUT_DATE__VALUE] = election_dict[ELECTION_JSON_KEY__DATE]
        if ELECTION_JSON_WEBFORM_KEY__TIME in election_dict:
            context[INPUT_TIME__VALUE] = election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
        if ELECTION_JSON_KEY__ELECTION_TYPE in election_dict:
            context[SELECTED_ELECTION_TYPE__HTML_NAME] = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
        if ELECTION_JSON_KEY__WEBSURVEY in election_dict:
            context[CURRENT_WEBSURVEY_LINK] = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
        if ELECTION_JSON_KEY__NOMINEES in election_dict:
            context[NOMINEES_HTML__NAME] = election_dict[ELECTION_JSON_KEY__NOMINEES]
    logger.info("[elections/create_webform_context.py create_webform_election_context_"
                "from_user_inputted_election_dict()] "
                f"created context of '{context}'")
    return context


def create_webform_election_context_from_db_election_obj(election_id):
    """
    Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    a dict that contains either the error experienced when trying to access the election id
    or the election itself in a format that is ready for the webform page to display
    """
    election = get_existing_election_by_id(election_id)
    context = {}
    if election is None:
        context.update({ERROR_MESSAGES_KEY: ["No valid election found for given election id"]})
    else:
        context.update({
            INPUT_ELECTION_ID__NAME: ELECTION_ID,
            INPUT_ELECTION_ID__VALUE: election.id,
            INPUT_DATE__VALUE: election.date.strftime(DATE_FORMAT),
            INPUT_TIME__VALUE: election.date.strftime(TIME_FORMAT),
            SELECTED_ELECTION_TYPE__HTML_NAME: election.election_type,
            CURRENT_WEBSURVEY_LINK: election.websurvey,
            NOMINEES_HTML__NAME: get_election_nominees(election)
        })
    logger.info("[elections/create_webform_context.py create_webform_election_context_from_db_election_obj()] "
                f"created context of '{context}'")
    return context
