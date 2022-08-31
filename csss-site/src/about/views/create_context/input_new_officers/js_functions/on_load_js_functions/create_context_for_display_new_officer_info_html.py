from about.views.Constants import INPUT_NEW_OFFICER_ID__NAME, INCLUDE_ID_FOR_NEW_OFFICER_IN_WEBFORM_HTML_NAME, \
    POSITIONS_NAME_KEY, ID_KEY, NEW_OFFICERS__HTML__NAME, NEW_OFFICERS__HTML_VALUE, \
    INPUT_RESEND_LINK_TO_OFFICER__HTML_VALUE, INPUT_RESEND_LINK_TO_OFFICER__HTML_NAME
from about.views.create_context.input_new_officers.js_functions.on_load_js_functions.\
    variable_is_non_empty_list import \
    variable_is_non_empty_list


def create_context_for_display_new_officer_info_html(context, officer_emaillist_and_position_mappings,
                                                     draft_new_officers=None):
    """
    Populates the context dictionary that will be used by
    about/templates/about/input_new_officers/js_functions/on_load_js_functions/display_new_officer_info.html

    Keyword Argyments
    context -- the context dictionary that has to be populated for display_new_officer_info.html
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    draft_new_officers -- the draft of the new officers that the user is trying to save or the saved officers
    """
    # defined in
    # csss-site/src/about/views/input_new_officers/js_functions/
    # on_load_js_functions/create_context_for_main_function_html.py or
    # csss-site/src/about/templates/about/input_new_officers/js_functions/add_new_officer.html
    # re_use_start_date
    # overwrite_current_officer
    # selected_position
    # position_name

    # defined in
    # about/views/input_new_officers/specify_new_officers/js_functions/on_load_js_functions/
    #  create_context_for_main_function_html.py or
    # about/views/create_context/specify_new_officers/create_context_for_specify_new_officers_html.py
    # term
    context[NEW_OFFICERS__HTML__NAME] = NEW_OFFICERS__HTML_VALUE
    saved_new_officers_exist = (
        variable_is_non_empty_list(draft_new_officers) and
        some_new_officers_already_saved(draft_new_officers)
    )
    if saved_new_officers_exist:
        context[INPUT_NEW_OFFICER_ID__NAME] = ID_KEY
        context[INCLUDE_ID_FOR_NEW_OFFICER_IN_WEBFORM_HTML_NAME] = True
    context[POSITIONS_NAME_KEY] = [
        position.position_name
        for position in officer_emaillist_and_position_mappings.filter(
            marked_for_deletion=False).order_by(
            'position_index')
    ]
    context[INPUT_RESEND_LINK_TO_OFFICER__HTML_NAME] = INPUT_RESEND_LINK_TO_OFFICER__HTML_VALUE


def some_new_officers_already_saved(draft_new_officers):
    return len([draft_new_officer for draft_new_officer in draft_new_officers if 'id' in draft_new_officer]) > 0
