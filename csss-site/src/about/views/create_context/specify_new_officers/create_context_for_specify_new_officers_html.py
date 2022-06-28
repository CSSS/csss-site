import datetime

from about.views.Constant_v2 import TERMS__HTML_NAME, CURRENT_TERM__HTML_NAME, YEARS__HTML_NAME, \
    CURRENT_YEAR__HTML_NAME, TERM__HTML_NAME, TERM_KEY, YEAR__HTML_NAME, YEAR_KEY
from about.views.input_new_officers.specify_new_officers.js_functions.\
    create_context_for_add_new_officer_html import \
    create_context_for_add_new_officer_html
from about.views.input_new_officers.specify_new_officers.js_functions.on_load_js_functions.\
    create_context_for_main_function_html import \
    create_context_for_main_function_html
from about.views.officer_position_and_github_mapping.officer_management_helper import TERM_SEASONS
from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html


def create_context_for_specify_new_officers_html(
        context, error_messages=None, term=None, year=None, draft_new_officers=None):
    if draft_new_officers is None:
        draft_new_officers = []
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    current_date = datetime.datetime.now()
    year_offset = 1
    if int(current_date.month) <= 4:
        term_season_index = 0
    elif int(current_date.month) <= 8:
        term_season_index = 1
    else:
        term_season_index = 2
        year_offset = 2

    context[TERMS__HTML_NAME] = TERM_SEASONS
    context[YEARS__HTML_NAME] = [
        year for year in reversed(list(range(1970, datetime.datetime.now().year + year_offset)))
    ]
    context[CURRENT_TERM__HTML_NAME] = TERM_SEASONS[term_season_index] if term is None else term
    context[CURRENT_YEAR__HTML_NAME] = current_date.year if year is None else year
    context[TERM__HTML_NAME] = TERM_KEY
    context[YEAR__HTML_NAME] = YEAR_KEY

    create_context_for_main_function_html(context, current_date=current_date, draft_new_officers=draft_new_officers)
    create_context_for_add_new_officer_html(context, current_date=current_date)
