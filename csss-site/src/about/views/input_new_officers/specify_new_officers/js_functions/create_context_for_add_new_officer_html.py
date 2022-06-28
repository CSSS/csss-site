import datetime

from about.views.Constant_v2 import START_DATE_VALUE, YEAR_MONTH_DAY_FORMAT
from about.views.input_new_officers.specify_new_officers.js_functions.on_load_js_functions.create_context_for_display_new_officer_info_html import \
    create_context_for_display_new_officer_info_html


def create_context_for_add_new_officer_html(context, current_date=None):
    context[START_DATE_VALUE] = datetime.datetime.now().strftime(YEAR_MONTH_DAY_FORMAT) \
        if current_date is None else current_date.strftime(YEAR_MONTH_DAY_FORMAT)
    create_context_for_display_new_officer_info_html(context)
