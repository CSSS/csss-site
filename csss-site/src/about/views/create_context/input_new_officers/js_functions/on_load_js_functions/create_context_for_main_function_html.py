from django.conf import settings
from django.forms import model_to_dict

from about.views.Constants import DRAFT_OR_FINALIZED_NEW_OFFICER_TO_DISPLAY__HTML_NAME, \
    NEW_OFFICERS__HTML_NAME, ID_KEY, DISCORD_ID_KEY, SFU_COMPUTING_ID_KEY, FULL_NAME_KEY, START_DATE_KEY, \
    POSITION_NAME_KEY, RE_USE_START_DATE_KEY, OVERWRITE_CURRENT_OFFICER_KEY, TERM_KEY, CHECKED, ON, FALSE_STRING, \
    TRUE_STRING, YEAR_MONTH_DAY_FORMAT, OFFICER_ENTER_INFO_URL, ENTER_NEW_OFFICER_INFO_URL, NUMBER_OF_NAGS_KEY
from about.views.create_context.input_new_officers.js_functions.on_load_js_functions. \
    create_context_for_display_new_officer_info_html import create_context_for_display_new_officer_info_html
from about.views.create_context.input_new_officers.js_functions.on_load_js_functions. \
    variable_is_non_empty_list import variable_is_non_empty_list


def create_context_for_main_function_html(context, saved_unprocessed_officers,
                                          officer_emaillist_and_position_mappings,
                                          current_date=None, draft_new_officers=None):
    """
    Populates the context dictionary that is used by
    about/templates/about/input_new_officers/js_functions/on_load_js_functions/main_function.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the main_function.html
    saved_unprocessed_officers -- the queryset of currently saved unprocessed officers
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    current_date -- the current date to be passed into the form that will be used if the user does not specify
     their own date for the new officers start date
    draft_new_officers -- the draft of the new officers that the user is trying to save or the saved officers
    """
    context[DRAFT_OR_FINALIZED_NEW_OFFICER_TO_DISPLAY__HTML_NAME] = FALSE_STRING

    url = f'http://{settings.HOST_ADDRESS}'
    if settings.DEBUG:
        url += f":{settings.PORT}"
    url += f'/login?next=/about/{ENTER_NEW_OFFICER_INFO_URL}'
    context[OFFICER_ENTER_INFO_URL] = url

    if draft_new_officers is None or len(draft_new_officers) == 0:
        draft_new_officers = [
            create_new_officer_model(draft_new_officer) for draft_new_officer in saved_unprocessed_officers
        ]

    else:
        draft_new_officers = [
            {
                ID_KEY: draft_new_officer.get(ID_KEY, ""),
                DISCORD_ID_KEY: draft_new_officer[DISCORD_ID_KEY],
                SFU_COMPUTING_ID_KEY: draft_new_officer[SFU_COMPUTING_ID_KEY],
                NUMBER_OF_NAGS_KEY: draft_new_officer.get(NUMBER_OF_NAGS_KEY, 0),
                FULL_NAME_KEY: draft_new_officer[FULL_NAME_KEY],

                START_DATE_KEY: draft_new_officer.get(START_DATE_KEY, current_date.strftime(YEAR_MONTH_DAY_FORMAT)),

                POSITION_NAME_KEY: draft_new_officer[POSITION_NAME_KEY],

                RE_USE_START_DATE_KEY: CHECKED if (
                    RE_USE_START_DATE_KEY in draft_new_officer and draft_new_officer[RE_USE_START_DATE_KEY] == ON
                ) else "",

                OVERWRITE_CURRENT_OFFICER_KEY: CHECKED
                if (
                    OVERWRITE_CURRENT_OFFICER_KEY in draft_new_officer and
                    draft_new_officer[OVERWRITE_CURRENT_OFFICER_KEY] == ON
                ) else "",

                TERM_KEY: draft_new_officer.get(TERM_KEY, "")

            }
            for draft_new_officer in draft_new_officers
        ]

    if variable_is_non_empty_list(draft_new_officers):
        context[NEW_OFFICERS__HTML_NAME] = draft_new_officers
        context[DRAFT_OR_FINALIZED_NEW_OFFICER_TO_DISPLAY__HTML_NAME] = TRUE_STRING
    create_context_for_display_new_officer_info_html(context, officer_emaillist_and_position_mappings,
                                                     draft_new_officers=draft_new_officers)
    return draft_new_officers


def create_new_officer_model(new_officer):
    new_officer = model_to_dict(new_officer)
    return {
        ID_KEY: new_officer[ID_KEY],
        DISCORD_ID_KEY: new_officer[DISCORD_ID_KEY],
        SFU_COMPUTING_ID_KEY: new_officer[SFU_COMPUTING_ID_KEY],
        NUMBER_OF_NAGS_KEY: new_officer[NUMBER_OF_NAGS_KEY],
        FULL_NAME_KEY: new_officer[FULL_NAME_KEY],
        START_DATE_KEY: new_officer[START_DATE_KEY].strftime(YEAR_MONTH_DAY_FORMAT),
        POSITION_NAME_KEY: new_officer[POSITION_NAME_KEY],
        RE_USE_START_DATE_KEY: CHECKED if (new_officer[RE_USE_START_DATE_KEY]) else "",
        OVERWRITE_CURRENT_OFFICER_KEY: CHECKED if (new_officer[OVERWRITE_CURRENT_OFFICER_KEY]) else "",
        TERM_KEY: new_officer[TERM_KEY]
    }
