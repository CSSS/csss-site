import datetime

from about.views.input_new_officers.js_functions.on_load_js_functions.\
    create_context_for_display_new_officer_info_html import \
    create_context_for_display_new_officer_info_html


def create_context_for_add_new_officer_html(context, current_date=None):
    context['start_date'] = datetime.datetime.now().strftime("%Y-%m-%d") \
        if current_date is None else current_date.strftime("%Y-%m-%d")
    create_context_for_display_new_officer_info_html(context)
