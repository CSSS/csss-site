from django.forms import model_to_dict

from about.models import NewOfficer
from about.views.Constant_v2 import SAVED_NOMINEES_EXIST, DRAFT_OR_FINALIZED_NEW_OFFICER_TO_DISPLAY__HTML_NAME, \
    NEW_OFFICERS__HTML_NAME, ID_KEY, DISCORD_ID_KEY, SFU_COMPUTING_ID_KEY, FULL_NAME_KEY, START_DATE_KEY, \
    POSITION_NAME_KEY, RE_USE_START_DATE_KEY, OVERWRITE_CURRENT_OFFICER_KEY, TERM_KEY, CHECKED, ON, FALSE_STRING, \
    TRUE_STRING, YEAR_MONTH_DAY_FORMAT
from about.views.input_new_officers.specify_new_officers.js_functions.on_load_js_functions.\
    create_context_for_display_new_officer_info_html import \
    create_context_for_display_new_officer_info_html, detected_draft_or_finalized_new_officers


def create_context_for_main_function_html(context, current_date=None, draft_new_officers=None):
    saved_nominees_exist = False
    if len(draft_new_officers) == 0:
        new_officers = NewOfficer.objects.all()
        saved_nominees_exist = len(new_officers) > 0
        draft_new_officers = [
            create_new_officer_model(draft_new_officer) for draft_new_officer in new_officers
        ]

    else:
        draft_new_officers = [
            {
                ID_KEY: draft_new_officer[ID_KEY] if ID_KEY in draft_new_officer else "",
                DISCORD_ID_KEY: draft_new_officer[DISCORD_ID_KEY],
                SFU_COMPUTING_ID_KEY: draft_new_officer[SFU_COMPUTING_ID_KEY],
                FULL_NAME_KEY: draft_new_officer[FULL_NAME_KEY],

                START_DATE_KEY: draft_new_officer[START_DATE_KEY]
                if START_DATE_KEY in draft_new_officer else current_date.strftime(YEAR_MONTH_DAY_FORMAT),

                POSITION_NAME_KEY: draft_new_officer[POSITION_NAME_KEY],

                RE_USE_START_DATE_KEY: CHECKED if (
                        RE_USE_START_DATE_KEY in draft_new_officer and draft_new_officer[RE_USE_START_DATE_KEY] == ON
                ) else "",

                OVERWRITE_CURRENT_OFFICER_KEY: CHECKED
                if (
                        OVERWRITE_CURRENT_OFFICER_KEY in draft_new_officer and
                        draft_new_officer[OVERWRITE_CURRENT_OFFICER_KEY] == ON
                ) else "",

                TERM_KEY: draft_new_officer[TERM_KEY] if TERM_KEY in draft_new_officer else ""

            }
            for draft_new_officer in draft_new_officers
        ]
    context[DRAFT_OR_FINALIZED_NEW_OFFICER_TO_DISPLAY__HTML_NAME] = FALSE_STRING
    context[SAVED_NOMINEES_EXIST] = saved_nominees_exist
    if detected_draft_or_finalized_new_officers(draft_new_officers):
        context[NEW_OFFICERS__HTML_NAME] = draft_new_officers
        context[DRAFT_OR_FINALIZED_NEW_OFFICER_TO_DISPLAY__HTML_NAME] = TRUE_STRING
    create_context_for_display_new_officer_info_html(context, draft_new_officers=draft_new_officers)


def create_new_officer_model(new_officer):
    new_officer = model_to_dict(new_officer)
    return {
        ID_KEY: new_officer[ID_KEY],
        DISCORD_ID_KEY: new_officer[DISCORD_ID_KEY],
        SFU_COMPUTING_ID_KEY: new_officer[SFU_COMPUTING_ID_KEY],
        FULL_NAME_KEY: new_officer[FULL_NAME_KEY],
        START_DATE_KEY: new_officer[START_DATE_KEY].strftime(YEAR_MONTH_DAY_FORMAT),
        POSITION_NAME_KEY: new_officer[POSITION_NAME_KEY],
        RE_USE_START_DATE_KEY: CHECKED if (new_officer[RE_USE_START_DATE_KEY]) else "",
        OVERWRITE_CURRENT_OFFICER_KEY: CHECKED if (new_officer[OVERWRITE_CURRENT_OFFICER_KEY]) else "",
        TERM_KEY: new_officer[TERM_KEY]
    }
