from csss.views.context_creation.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.webform.create_context_for_form__webform_html import \
    create_context_for_form__webform_html
from elections.views.create_context.webform.js_functions.create_context_for_add_blank_nominee_html import \
    create_context_for_add_blank_nominee_html
from elections.views.create_context.webform.js_functions.create_context_for_add_blank_speech_html import \
    create_context_for_add_blank_speech_html
from elections.views.create_context.webform.js_functions.on_load_js_function.create_context_for_main_function_html import \
    create_context_for_main_function_html


def create_context_for_create_election__webform_html(
        context, error_messages=None, election_dict=None, election_date=None, election_time=None, election_type=None,
        websurvey_link=None, webform_election=True, new_webform_election=True,
        include_id_for_nominee=False, draft_or_finalized_nominee_to_display=False, nominees_info=None,
):
    if election_dict is not None:
        if election_date is None and ELECTION_JSON_KEY__DATE in election_dict:
            election_date = election_dict[ELECTION_JSON_KEY__DATE]
        if election_time is None and ELECTION_JSON_WEBFORM_KEY__TIME in election_dict:
            election_time = election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
        if election_type is None and ELECTION_JSON_KEY__ELECTION_TYPE in election_dict:
            election_type = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
        if websurvey_link is None and ELECTION_JSON_KEY__WEBSURVEY in election_dict:
            websurvey_link = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
        if (
                nominees_info is None and ELECTION_JSON_KEY__NOMINEES in election_dict and
                type(election_dict[ELECTION_JSON_KEY__NOMINEES]) is list):
            nominees_info = election_dict[ELECTION_JSON_KEY__NOMINEES]
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    create_context_for_form__webform_html(
        context, election_date=election_date, election_time=election_time,
        election_type=election_type, websurvey_link=websurvey_link,
        create_new_election=new_webform_election
    )
    create_context_for_main_function_html(
        context, webform_election=webform_election, new_webform_election=new_webform_election,
        include_id_for_nominee=include_id_for_nominee,
        draft_or_finalized_nominee_to_display=draft_or_finalized_nominee_to_display, nominees_info=nominees_info
    )
    create_context_for_add_blank_nominee_html(
        context, webform_election=webform_election, new_webform_election=new_webform_election,
        include_id_for_nominee=include_id_for_nominee,
        draft_or_finalized_nominee_to_display=draft_or_finalized_nominee_to_display
    )
    create_context_for_add_blank_speech_html(context)
