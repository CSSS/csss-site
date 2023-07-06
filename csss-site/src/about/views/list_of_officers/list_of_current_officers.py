from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.models import Officer, Term
from about.views.Constants import TAB_STRING
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.send_discord_dm import send_discord_dm
from csss.views_helper import get_current_term

OFFICER_ID_HTML_URL_PARAMETER_KEY = 'officer_id_key'
OFFICER_ID_HTML_URL_PARAMETER_VALUE = 'officer_id'

NEW_PASSWORD_KEY = "password_key"
NEW_PASSWORD_VALUE = 'password'

UPDATE_BITWARDEN_PASSWORD_BUTTON__HTML_NAME_KEY = 'update_bitwarden_password_key'
UPDATE_BITWARDEN_PASSWORD_BUTTON__HTML_NAME_VALUE = 'update_bitwarden_password'


def list_of_current_officers(request):
    """
    Lists all current CSSS Officers
    """
    if UPDATE_BITWARDEN_PASSWORD_BUTTON__HTML_NAME_VALUE in request.POST:
        officer = Officer.objects.get(id=request.GET[OFFICER_ID_HTML_URL_PARAMETER_VALUE])
        new_password = request.POST[NEW_PASSWORD_VALUE]
        officer._bitwarden_takeover_needed = False
        officer.save()
        send_discord_dm(
            officer.discord_id, "Bitwarden Password Reset",
            f"URL: https://vault.bitwarden.com/#/login\n\n username: "
            f"`{officer.sfu_officer_mailing_list_email}`\n\npassword : `{new_password}`"
        )
        return HttpResponseRedirect(request.path)
    context = create_main_context(request, TAB_STRING)
    officer_map = {}
    show_all_officers = context['root_user'] or context['officer_in_past_5_terms']
    officers = Officer.objects.all().filter(elected_term=get_current_term()).order_by(
        'position_index', 'start_date'
    )
    for officer in officers:
        if officer.elected_term not in officer_map:
            officer_map[officer.elected_term] = {}
        if officer.position_name not in officer_map[officer.elected_term]:
            officer_map[officer.elected_term][officer.position_name] = []
        if officer not in officer_map[officer.elected_term][officer.position_name]:
            if len(officer_map[officer.elected_term][officer.position_name]) == 0:
                officer_map[officer.elected_term][officer.position_name] = [[officer]]
            else:
                number_of_times_position_has_changed_hands_so_far_for_specified_term = (
                    len(officer_map[officer.elected_term][officer.position_name]) - 1
                )
                officer_from_last_iteration = officer_map[officer.elected_term][officer.position_name][number_of_times_position_has_changed_hands_so_far_for_specified_term][0] # noqa E501
                if officer_from_last_iteration.start_date == officer.start_date:
                    officer_map[officer.elected_term][officer.position_name][number_of_times_position_has_changed_hands_so_far_for_specified_term].append(officer) # noqa E501
                else:
                    if show_all_officers:
                        officer_map[officer.elected_term][officer.position_name].append([officer])
                    else:
                        officer_map[officer.elected_term][officer.position_name] = [[officer]]
    context.update({
        'officer_map': officer_map,
        'term_active': get_current_term(),
        'terms': [Term.objects.all().filter(term_number=get_current_term()).first()],
        OFFICER_ID_HTML_URL_PARAMETER_KEY: OFFICER_ID_HTML_URL_PARAMETER_VALUE,
        NEW_PASSWORD_KEY: NEW_PASSWORD_VALUE,
        UPDATE_BITWARDEN_PASSWORD_BUTTON__HTML_NAME_KEY: UPDATE_BITWARDEN_PASSWORD_BUTTON__HTML_NAME_VALUE
    })

    return render(request, 'about/list_of_officers.html', context)
