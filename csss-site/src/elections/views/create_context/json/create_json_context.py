import json

from about.models import OfficerEmailListAndPositionMapping
from csss.setup_logger import Loggers
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import DATE_FORMAT
from elections.models import Election
from elections.views.Constants import TYPES_OF_ELECTIONS, VALID_POSITION_NAMES, \
    FORMAT_ELECTION_JSON__DIV_ID_NAME, \
    JS_FORMATTING_ERROR, USER_INPUTTED_ELECTION_JSON__KEY, ELECTION_JSON__KEY, DATE_AND_TIME_FORMAT, \
    SAVE_NEW_JSON_ELECTION__BUTTON_ID, SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE, \
    SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID, \
    SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE, DISPLAY_INSTRUCTIONS_TO_VALID_JSON__CLASS_NAME, \
    DISPLAY_INSTRUCTIONS_TO_VALID_JSON
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__END_DATE, \
    ELECTION_JSON_VALUE__DATE_FORMAT
from elections.views.create_context.submission_buttons_context import create_base_submission_buttons_context
from elections.views.extractors.get_election_nominees import get_election_nominees


def create_json_election_context_from_user_inputted_election_dict(
        error_message=None, election_information=None, create_new_election=True):
    """
    Creating context for JSON pages for election creation or modification

    Keyword Argument
    error_message - the error message to transfer to the context that is returned
    election_information - the election json that is transferred to the context that is returned
    create_new_election -- indicates whether the submission buttons should be saving key for creating election
     or updating an election

    Return
    a dict with the following keys
    {
        "types_of_elections" : "Options for...."
        "valid_position_names" : "Valid Positions: ...."
        "json_formatting_div__name", election_input__html_name
        "error_messages"
        "election"
    }
    the dict will also contain the keys created by create_submission_buttons_context for new elections
    """
    logger = Loggers.get_logger()
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    current_positions = [
        position.position_name for position in OfficerEmailListAndPositionMapping.objects.all().filter(
            marked_for_deletion=False, elected_via_election_officer=True
        )
    ]
    context = {
        TYPES_OF_ELECTIONS: f"Options for \"{ELECTION_JSON_KEY__ELECTION_TYPE}\": "
                            f"{', '.join(valid_election_type_choices)}",
        VALID_POSITION_NAMES: f"Valid Positions: {', '.join(current_positions)}",
        FORMAT_ELECTION_JSON__DIV_ID_NAME: JS_FORMATTING_ERROR,
        USER_INPUTTED_ELECTION_JSON__KEY: ELECTION_JSON__KEY
    }
    if error_message is not None:
        context[ERROR_MESSAGES_KEY] = [error_message]
    if election_information is not None:
        context[ELECTION_JSON__KEY] = json.dumps(election_information)
    context.update(create_json_submission_buttons_context(create_new_election=create_new_election))
    logger.info("[elections/create_json_context.py create_json_election_context_from_user_inputted_election_dict()] "
                f"created context of '{context}'")
    return context


def create_json_election_context_from_db_election_obj(election):
    """
    Returns information about the election

    Keyword Argument
    election -- the election whose information is used to populate the dict

    Return
    a dict that contains the election itself in a format that is ready for the json page to display
    """
    logger = Loggers.get_logger()
    context = {
        ELECTION_JSON_KEY__ELECTION_TYPE: election.election_type,
        ELECTION_JSON_KEY__DATE: election.date.strftime(DATE_AND_TIME_FORMAT),
        ELECTION_JSON_KEY__END_DATE: election.end_date.strftime(DATE_FORMAT)
        if election.end_date is not None else ELECTION_JSON_VALUE__DATE_FORMAT,
        ELECTION_JSON_KEY__WEBSURVEY: election.websurvey,
        ELECTION_JSON_KEY__NOMINEES: get_election_nominees(election)
    }
    logger.info("[elections/create_json_context.py create_json_election_context_from_db_election_obj()] "
                f"created election context of '{context}'")
    return context


def create_json_submission_buttons_context(create_new_election=True):
    """
    creates the context keys needed to populate the button for saving a new election or modifications to the
     existing election on the JSON pages

    Keyword Argument
    create_new_election -- default of True. used to indicate if the election has to use a value of "create_election"
     or "update_election"

    Return
    a dict that contains the following keys
    - input_redirect_election_submit__name
    - save_election__button_id
    - input_redirect_election_submit__value
    - save_new_election_and_continue_editing__button_id
    - input_redirect_election_submit_and_continue_editing__value
    """
    logger = Loggers.get_logger()
    context = create_base_submission_buttons_context(create_new_election=create_new_election)
    context.update({
        SAVE_NEW_JSON_ELECTION__BUTTON_ID: SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE,
        SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID:
            SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE,
        DISPLAY_INSTRUCTIONS_TO_VALID_JSON__CLASS_NAME: DISPLAY_INSTRUCTIONS_TO_VALID_JSON
    })
    logger.info("[elections/submission_buttons_context.py create_json_submission_buttons_context()] "
                f"created election context of '{context}'")
    return context
