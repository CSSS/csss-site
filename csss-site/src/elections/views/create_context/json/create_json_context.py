import json
import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import TYPES_OF_ELECTIONS, VALID_POSITION_NAMES, \
    FORMAT_ELECTION_JSON__DIV_ID_NAME, \
    JS_FORMATTING_ERROR, USER_INPUTTED_ELECTION_JSON__KEY, ELECTION_JSON__KEY, DATE_AND_TIME_FORMAT, \
    INDICATE_IF_JSON_ELECTION_HTML
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.submission_buttons_context import create_submission_buttons_context
from elections.views.extractors.get_election_nominees import get_election_nominees

logger = logging.getLogger('csss_site')


def create_json_election_context_from_user_inputted_election_dict(
        error_message=None, election_information=None, create_new_election=True):
    """
    Creating context for JSON pages for election creation or modification

    Keyword Argument
    election_id - the ID to transfer to the context that is returned
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
        USER_INPUTTED_ELECTION_JSON__KEY: ELECTION_JSON__KEY,
        INDICATE_IF_JSON_ELECTION_HTML: True
    }
    if error_message is not None:
        context[ERROR_MESSAGES_KEY] = [error_message]
    if election_information is not None:
        context[ELECTION_JSON__KEY] = json.dumps(election_information)
    context.update(create_submission_buttons_context(create_new_election=create_new_election))
    logger.info("[elections/create_json_context.py create_json_election_context_from_user_inputted_election_dict()] "
                f"created context of '{context}'")
    return context


def create_json_election_context_from_db_election_obj(election):
    """
    Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    a dict that contains the election itself in a format that is ready for the json page to display
    """
    context = {
        ELECTION_JSON_KEY__ELECTION_TYPE: election.election_type,
        ELECTION_JSON_KEY__DATE: election.date.strftime(DATE_AND_TIME_FORMAT),
        ELECTION_JSON_KEY__WEBSURVEY: election.websurvey,
        ELECTION_JSON_KEY__NOMINEES: get_election_nominees(election)
    }
    logger.info("[elections/create_json_context.py create_json_election_context_from_db_election_obj()] "
                f"created election context of '{context}'")
    return context
