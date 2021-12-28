from elections.views.Constants import SAVE_NEW_NOMINEE__BUTTON_ID, SAVE_NEW_NOMINEE__BUTTON_ID_VALUE, \
    INPUT_REDIRECT_NOMINEE__NAME, CREATE_OR_UPDATE_NOMINEE__NAME, INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE, \
    SAVE_OR_UPDATE_NOMINEE__VALUE, NOMINEE_DIV__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE


def create_context_for_form__nominee_links_html(context):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/js_functions/add_blank_speech.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the add_blank_speech.html
    """
    context.update({
        SAVE_NEW_NOMINEE__BUTTON_ID: SAVE_NEW_NOMINEE__BUTTON_ID_VALUE,
        INPUT_REDIRECT_NOMINEE__NAME: CREATE_OR_UPDATE_NOMINEE__NAME,
        INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE: SAVE_OR_UPDATE_NOMINEE__VALUE,
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
    })
