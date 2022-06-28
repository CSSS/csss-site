from about.models import OfficerEmailListAndPositionMapping
from about.views.Constant_v2 import INPUT_NEW_OFFICER_ID__NAME, INCLUDE_ID_FOR_NEW_OFFICER_IN_WEBFORM_HTML_NAME, \
    POSITIONS_NAME_KEY, ID_KEY, NEW_OFFICERS__HTML__NAME, NEW_OFFICERS__HTML_VALUE


def create_context_for_display_new_officer_info_html(context, draft_new_officers=None):
    # defined in
    # csss-site/src/about/views/input_new_officers/js_functions/on_load_js_functions/create_context_for_main_function_html.py or
    # csss-site/src/about/templates/about/input_new_officers/js_functions/add_new_officer.html
    # re_use_start_date
    # overwrite_current_officer
    # selected_position

    if detected_draft_or_finalized_new_officers(draft_new_officers) and some_new_officers_already_saved(draft_new_officers):
        context[INPUT_NEW_OFFICER_ID__NAME] = ID_KEY
        context[INCLUDE_ID_FOR_NEW_OFFICER_IN_WEBFORM_HTML_NAME] = True
    context[NEW_OFFICERS__HTML__NAME] = NEW_OFFICERS__HTML_VALUE
    context[POSITIONS_NAME_KEY] = [
        position.position_name
        for position in OfficerEmailListAndPositionMapping.objects.all().filter(
            marked_for_deletion=False).order_by(
            'position_index')
    ]


def detected_draft_or_finalized_new_officers(draft_new_officers):
    return type(draft_new_officers) is list and len(draft_new_officers) > 0


def some_new_officers_already_saved(draft_new_officers):
    return len([draft_new_officer for draft_new_officer in draft_new_officers if 'id' in draft_new_officer]) > 0
