from csss.setup_logger import get_logger
from elections.views.Constants import CREATE_NEW_ELECTION__NAME, \
    INPUT_REDIRECT_ELECTION_SUBMIT__VALUE, SAVE_ELECTION__VALUE, \
    INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE, \
    UPDATE_EXISTING_ELECTION__NAME, INPUT_REDIRECT_ELECTION_SUBMIT__NAME


def create_base_submission_buttons_context(create_new_election=True):
    """
    creates the context keys needed to populate the button for saving a new election or modifications to the
     existing election on either JSON or Webform pages

    Keyword Argument
    create_new_election -- default of True. used to indicate if the election has to use a value of "create_election"
     or "update_election"

    Return
    a dict that contains the following keys
    - input_redirect_election_submit__name
    - input_redirect_election_submit__value
    - input_redirect_election_submit_and_continue_editing__value
    """
    logger = get_logger()
    if create_new_election:
        context = {
            INPUT_REDIRECT_ELECTION_SUBMIT__NAME: CREATE_NEW_ELECTION__NAME
        }
    else:
        context = {
            INPUT_REDIRECT_ELECTION_SUBMIT__NAME: UPDATE_EXISTING_ELECTION__NAME
        }
    context.update({
        INPUT_REDIRECT_ELECTION_SUBMIT__VALUE: SAVE_ELECTION__VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE: SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE,
    })
    logger.info(
        "[elections/submission_buttons_context.py create_base_submission_buttons_context()] "
        f"created election context of'{context}'"
    )
    return context
