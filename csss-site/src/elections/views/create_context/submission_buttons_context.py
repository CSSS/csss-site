import logging

from elections.views.Constants import INPUT_REDIRECT_ELECTION__NAME, CREATE_NEW_ELECTION__NAME, \
    INPUT_REDIRECT_ELECTION_SUBMIT__VALUE, SAVE_ELECTION__VALUE, \
    INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE, \
    UPDATE_EXISTING_ELECTION__NAME, SAVE_NEW_JSON_ELECTION__BUTTON_ID, SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE, \
    SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID, \
    SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE

logger = logging.getLogger('csss_site')


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
    if create_new_election:
        context = {
            INPUT_REDIRECT_ELECTION__NAME: CREATE_NEW_ELECTION__NAME
        }
    else:
        context = {
            INPUT_REDIRECT_ELECTION__NAME: UPDATE_EXISTING_ELECTION__NAME
        }
    context.update({
        SAVE_NEW_JSON_ELECTION__BUTTON_ID: SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE,
        SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID:
            SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT__VALUE: SAVE_ELECTION__VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE: SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE,
    })
    logger.info("[elections/submission_buttons_context.py create_submission_buttons_context()] "
                f"created election context of '{context}'")
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
    if create_new_election:
        context = {
            INPUT_REDIRECT_ELECTION__NAME: CREATE_NEW_ELECTION__NAME
        }
    else:
        context = {
            INPUT_REDIRECT_ELECTION__NAME: UPDATE_EXISTING_ELECTION__NAME
        }
    context.update({
        INPUT_REDIRECT_ELECTION_SUBMIT__VALUE: SAVE_ELECTION__VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE: SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE,
    })
    logger.info("[elections/submission_buttons_context.py create_submission_buttons_context()] "
                f"created election context of '{context}'")
    return context
