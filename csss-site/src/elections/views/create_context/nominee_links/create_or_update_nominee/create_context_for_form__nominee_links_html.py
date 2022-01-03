from elections.views.Constants import \
    CREATE_OR_UPDATE_NOMINEE__NAME, INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE, \
    SAVE_OR_UPDATE_NOMINEE__VALUE, NOMINEE_DIV__NAME, INPUT_REDIRECT_NOMINEE_SUBMIT__NAME, SAVE_NOMINEE__BUTTON_ID, \
    SAVE_NOMINEE__BUTTON_ID_VALUE
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE


def create_context_for_form__nominee_links_html(context):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_nominee/form__nominee_links.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the form__nominee_links.html
    """
    context.update({
        SAVE_NOMINEE__BUTTON_ID: SAVE_NOMINEE__BUTTON_ID_VALUE,
        INPUT_REDIRECT_NOMINEE_SUBMIT__NAME: CREATE_OR_UPDATE_NOMINEE__NAME,
        INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE: SAVE_OR_UPDATE_NOMINEE__VALUE,
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
    })
