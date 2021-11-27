import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import INPUT_DATE__NAME, \
    INPUT_DATE__VALUE, INPUT_TIME__NAME, INPUT_TIME__VALUE, SELECT_ELECTION_TYPE__NAME, \
    SELECTED_ELECTION_TYPE__HTML_NAME, CREATE_NEW_ELECTION__HTML_NAME, NOMINEES_HTML__NAME, CURRENT_WEBSURVEY_LINK, \
    NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH__NAME, INPUT_NOMINEE_FACEBOOK__NAME, \
    INPUT_NOMINEE_LINKEDIN__NAME, INPUT_NOMINEE_EMAIL__NAME, INPUT_NOMINEE_DISCORD__NAME, \
    INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, INPUT_NOMINEE_POSITION_NAMES__NAME, CURRENT_ELECTION_TYPES, \
    INPUT_WEBSURVEY__NAME, INPUT_NOMINEE_NAME__NAME, CURRENT_OFFICER_POSITIONS, DATE_FORMAT, TIME_FORMAT, \
    INPUT_NOMINEE_ID__NAME, ID_KEY, INPUT_SPEECH_ID__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, \
    ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOMINEE
from elections.views.create_context.submission_buttons_context import create_base_submission_buttons_context
from elections.views.create_context.webform_format.create_context_for_display_nominee_info_html import \
    create_context_for_display_nominee_info_html
from elections.views.extractors.get_election_nominees import get_election_nominees

logger = logging.getLogger('csss_site')


def create_webform_context(
        create_new_election=True, nominee_obj=None, nominee_info=None, include_id_for_nominee=True):
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
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        INPUT_SPEECH_ID__NAME: ID_KEY,

        CREATE_NEW_ELECTION__HTML_NAME: create_new_election,

    }
    context.update(create_webform_submission_buttons_context(create_new_election=create_new_election))
    create_context_for_main_function_html(
        context, nominee_obj=nominee_obj, nominee_info=nominee_info, include_id_for_nominee=include_id_for_nominee,
        create_new_election=create_new_election
    )
    create_context_for_add_blank_nominee_html(context)
    logger.info("[elections/create_webform_context.py create_webform_context()] "
                f"created context of '{context}'")
    return context


def create_webform_election_context_from_user_inputted_election_dict(
        error_message, nominee_obj=None, nominee_info=None, include_id_for_nominee=True, create_new_election=None,
        election_dict=None):
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
    create_context_for_main_function_html(
        context, nominee_obj=nominee_obj, nominee_info=nominee_info, include_id_for_nominee=include_id_for_nominee,
        create_new_election=create_new_election
    )
    create_context_for_add_blank_nominee_html(context)

    logger.info("[elections/create_webform_context.py create_webform_election_context_"
                "from_user_inputted_election_dict()] "
                f"created context of '{context}'")
    return context


def create_context_for_add_blank_nominee_html(context):
    create_context_for_display_nominee_info_html(context)


def create_webform_election_context_from_db_election_obj(
        election, create_new_election=True, nominee_obj=None, nominee_info=None, include_id_for_nominee=True):
    """
    Returns information about the election

    Keyword Argument
    election -- the election whose information is used to populate the dict

    Return
    a dict that contains the election itself in a format that is ready for the webform page to display
    """
    context = {
        INPUT_DATE__VALUE: election.date.strftime(DATE_FORMAT),
        INPUT_TIME__VALUE: election.date.strftime(TIME_FORMAT),
        SELECTED_ELECTION_TYPE__HTML_NAME: election.election_type,
        CURRENT_WEBSURVEY_LINK: election.websurvey,
        NOMINEES_HTML__NAME: get_election_nominees(election)
    }
    create_context_for_add_blank_nominee_html(context)
    create_context_for_main_function_html(
        context, nominee_obj=nominee_obj, nominee_info=nominee_info, include_id_for_nominee=include_id_for_nominee,
        create_new_election=create_new_election
    )
    logger.info("[elections/create_webform_context.py create_webform_election_context_from_db_election_obj()] "
                f"created context of '{context}'")
    return context


def create_webform_submission_buttons_context(create_new_election=True):
    """
    creates the context keys needed to populate the button for saving a new election or modifications to the
     existing election on the WebForm pages

    Keyword Argument
    create_new_election -- default of True. used to indicate if the election has to use a value of "create_election"
     or "update_election"

    Return
    a dict that contains the following keys
    - input_redirect_election_submit__name
    - input_redirect_election_submit__value
    - input_redirect_election_submit_and_continue_editing__value
    """
    return create_base_submission_buttons_context(create_new_election=create_new_election)


def create_context_for_main_function_html(
        context, nominee_obj=None, nominee_info=None, include_id_for_nominee=True, create_new_election=None):
    context.update({NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE})
    if ELECTION_JSON_KEY__NOMINEES in nominee_info:
        context[NOMINEES_HTML__NAME] = nominee_info[ELECTION_JSON_KEY__NOMINEES]
    create_context_for_display_nominee_info_html(
        context, nominee_obj=nominee_obj, nominee_info=nominee_info,
        include_id_for_nominee=-include_id_for_nominee, create_new_election=create_new_election
    )
