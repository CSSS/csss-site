import datetime

from about.views.input_new_officers.js_functions.create_context_for_add_new_officer_html import \
    create_context_for_add_new_officer_html
from about.views.input_new_officers.js_functions.on_load_js_functions.create_context_for_main_function_html import \
    create_context_for_main_function_html
from about.views.officer_position_and_github_mapping.officer_management_helper import TERM_SEASONS
from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html


def create_context_for_specify_new_officers_html(
        context, error_messages=None, term=None, year=None, draft_new_officers=None):
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

    context['terms__html_name'] = TERM_SEASONS
    context['years__html_name'] = [
        year for year in reversed(list(range(1970, datetime.datetime.now().year + year_offset)))
    ]
    context['current_term__html_name'] = TERM_SEASONS[term_season_index] if term is None else term
    context['current_year__html_name'] = current_date.year if year is None else year

    create_context_for_main_function_html(context, current_date=current_date, draft_new_officers=draft_new_officers)
    create_context_for_add_new_officer_html(context, current_date=current_date)
