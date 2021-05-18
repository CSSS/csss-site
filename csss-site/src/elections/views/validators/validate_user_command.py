from elections.views.Constants import CREATE_NEW_ELECTION__NAME, SAVE_ELECTION__VALUE, \
    SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE, UPDATE_EXISTING_ELECTION__NAME


def validate_user_command(request, create_new_election=True):
    if create_new_election:
        return (
                CREATE_NEW_ELECTION__NAME in request.POST and
                request.POST[CREATE_NEW_ELECTION__NAME] in [
                    SAVE_ELECTION__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE
                ]
        )
    else:
        return (
                UPDATE_EXISTING_ELECTION__NAME in request.POST and
                request.POST[UPDATE_EXISTING_ELECTION__NAME] in [
                    SAVE_ELECTION__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE
                ]
        )
