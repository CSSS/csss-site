import datetime

from about.views.Constants import START_DATE_VALUE, YEAR_MONTH_DAY_FORMAT
from about.views.create_context.input_new_officers.js_functions.on_load_js_functions.\
    create_context_for_display_new_officer_info_html import \
    create_context_for_display_new_officer_info_html
from csss.setup_logger import date_timezone


def create_context_for_add_new_officer_html(context, officer_emaillist_and_position_mappings, current_date=None):
    """
    Populates the context dictionary that is used by
     about/templates/about/input_new_officers/js_functions/add_new_officer.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the add_new_officer.html
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    currrent_date -- the current date to use as a placeholder for any new officers
    """
    context[START_DATE_VALUE] = datetime.datetime.now(date_timezone).strftime(YEAR_MONTH_DAY_FORMAT) \
        if current_date is None else current_date.strftime(YEAR_MONTH_DAY_FORMAT)
    create_context_for_display_new_officer_info_html(context, officer_emaillist_and_position_mappings)
