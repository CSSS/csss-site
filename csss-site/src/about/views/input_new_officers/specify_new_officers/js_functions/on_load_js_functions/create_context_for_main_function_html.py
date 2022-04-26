from django.forms import model_to_dict

from about.models import NewOfficer
from about.views.input_new_officers.specify_new_officers.js_functions.on_load_js_functions.create_context_for_display_new_officer_info_html import \
    create_context_for_display_new_officer_info_html, detected_draft_or_finalized_new_officers


def create_context_for_main_function_html(context, current_date=None, draft_new_officers=None):
    saved_nominees_exist = False
    if draft_new_officers is None:
        new_officers = NewOfficer.objects.all()
        saved_nominees_exist = len(new_officers) > 0
        draft_new_officers = [
            create_new_officer_model(draft_new_officer) for draft_new_officer in new_officers
        ]

    else:
        draft_new_officers = [
            {
                "id": draft_new_officer['id'] if "id" in draft_new_officer else "",
                'discord_id': draft_new_officer['discord_id'],
                'sfu_computing_id': draft_new_officer['sfu_computing_id'],
                'full_name': draft_new_officer['full_name'],

                'start_date': draft_new_officer['start_date']
                if 'start_date' in draft_new_officer else current_date.strftime("%Y-%m-%d"),

                'position_name': draft_new_officer['position_name'],

                're_use_start_date': "checked" if (
                        're_use_start_date' in draft_new_officer and draft_new_officer['re_use_start_date'] == "on"
                ) else "",

                'overwrite_current_officer': "checked"
                if (
                        'overwrite_current_officer' in draft_new_officer and
                        draft_new_officer['overwrite_current_officer'] == "on"
                ) else "",

                "term": draft_new_officer['term'] if 'term' in draft_new_officer else ""

            }
            for draft_new_officer in draft_new_officers
        ]
    context['draft_or_finalized_new_officer_to_display__html_name'] = 'false'
    context['saved_nominees_exist'] = saved_nominees_exist
    if detected_draft_or_finalized_new_officers(draft_new_officers):
        context['new_officers__html_name'] = draft_new_officers
        context['draft_or_finalized_new_officer_to_display__html_name'] = 'true'
    create_context_for_display_new_officer_info_html(context, draft_new_officers=draft_new_officers)


def create_new_officer_model(new_officer):
    new_officer = model_to_dict(new_officer)
    return {
        "id": new_officer['id'],
        'discord_id': new_officer['discord_id'],
        'sfu_computing_id': new_officer['sfu_computing_id'],
        'full_name': new_officer['full_name'],
        'start_date': new_officer['start_date'].strftime("%Y-%m-%d"),
        'position_name': new_officer['position_name'],
        're_use_start_date': "checked" if (new_officer['re_use_start_date']) else "",
        'overwrite_current_officer': "checked" if (new_officer['overwrite_current_officer']) else "",
        "term": new_officer['term']
    }
