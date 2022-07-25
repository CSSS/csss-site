import datetime

from about.views.Constants import TERMS__HTML_NAME, YEARS__HTML_NAME, CURRENT_TERM__HTML_NAME, \
    CURRENT_YEAR__HTML_NAME, TERM__HTML_NAME, YEAR__HTML_NAME, TERM_KEY, YEAR_KEY, SAVED_NOMINEES_EXIST, \
    NEW_OFFICERS__HTML_NAME, SAVE_OR_CREATE_ALL_NEW_OFFICERS_INFORMATION, \
    INPUT_REDIRECT_SAVE_OR_UPDATE_NEW_OFFICERS_SUBMIT_AND_CONTINUE_EDITING_VALUE, \
    INPUT_REDIRECT_SAVE_OR_UPDATE_NEW_OFFICERS_SUBMIT_NAME, SAVE_OR_UPDATE_NEW_OFFICERS_NAME, \
    NEW_OFFICERS_DIV_ID__HTML_NAME, NEW_OFFICERS_DIV_ID
from about.views.create_context.input_new_officers.js_functions.create_context_for_add_new_officer_html import \
    create_context_for_add_new_officer_html
from about.views.create_context.input_new_officers.js_functions.on_load_js_functions.create_context_for_main_function_html import \
    create_context_for_main_function_html
from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from csss.views_helper import TERM_SEASONS


def create_context_for_specify_new_officers_html(
    context, saved_unprocessed_officers, officer_emaillist_and_position_mappings, error_messages=None, term=None,
    year=None, draft_new_officers=None):
    """
    Populate the context dictionary that is used by
    about/templates/about/input_new_officers/specify_new_officers.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the specify_new_officers.html
    saved_unprocessed_officers -- the queryset of currently saved unprocessed officers
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    error_messages -- error message to display
    term -- the currently selected term that will be used if there are no saved new_officers
    year -- the currently selected year that will be used if there are no saved new_officers
    draft_new_officers -- the draft of the new officers that the user is trying to save

    """
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)

    context[TERM__HTML_NAME] = TERM_KEY
    context[TERMS__HTML_NAME] = TERM_SEASONS

    current_date = datetime.datetime.now()
    current_year_offset = 1
    if int(current_date.month) <= 4:
        term_season_index = 0
    elif int(current_date.month) <= 8:
        term_season_index = 1
    else:
        term_season_index = 2
        current_year_offset = 2

    if len(saved_unprocessed_officers) > 0:
        new_officer = saved_unprocessed_officers[0]
        term = new_officer.term.term
        year = new_officer.term.year

    context[CURRENT_TERM__HTML_NAME] = TERM_SEASONS[term_season_index] if term is None else term

    context[YEAR__HTML_NAME] = YEAR_KEY

    context[YEARS__HTML_NAME] = [
        year for year in reversed(list(range(1970, datetime.datetime.now().year + current_year_offset)))
    ]

    context[CURRENT_YEAR__HTML_NAME] = current_date.year if year is None else year

    context[INPUT_REDIRECT_SAVE_OR_UPDATE_NEW_OFFICERS_SUBMIT_NAME] = SAVE_OR_UPDATE_NEW_OFFICERS_NAME
    context[INPUT_REDIRECT_SAVE_OR_UPDATE_NEW_OFFICERS_SUBMIT_AND_CONTINUE_EDITING_VALUE] =\
        SAVE_OR_CREATE_ALL_NEW_OFFICERS_INFORMATION
    context[SAVED_NOMINEES_EXIST] = len(saved_unprocessed_officers) > 0
    context[NEW_OFFICERS_DIV_ID__HTML_NAME] = NEW_OFFICERS_DIV_ID

    new_officer_infos_to_display = create_context_for_main_function_html(
        context, saved_unprocessed_officers, officer_emaillist_and_position_mappings, current_date=current_date,
        draft_new_officers=draft_new_officers
    )
    context[NEW_OFFICERS__HTML_NAME] = new_officer_infos_to_display
    create_context_for_add_new_officer_html(context, officer_emaillist_and_position_mappings, current_date=current_date)
