from elections.views.Constants import CREATE_NEW_ELECTION__NAME, \
    UPDATE_EXISTING_ELECTION__NAME, INPUT_REDIRECT_ELECTION_SUBMIT__VALUE, SAVE_ELECTION__VALUE, \
    INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE, \
    INPUT_REDIRECT_ELECTION_SUBMIT__NAME


def create_context_for_submission_buttons_html(context, create_new_election=False):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/submission_buttons.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_nominee_names.html
    create_new_election -- boolean to indicate what the submission button should be labelled with
    """
    context.update({
        INPUT_REDIRECT_ELECTION_SUBMIT__NAME: CREATE_NEW_ELECTION__NAME if create_new_election
        else UPDATE_EXISTING_ELECTION__NAME,
        INPUT_REDIRECT_ELECTION_SUBMIT__VALUE: SAVE_ELECTION__VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE: SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE
    })
