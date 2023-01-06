from about.models import Officer, Term
from about.views.Constants import EMAIL_LIST_MAPPINGS, SFU_EMAIL_LIST, SFU_COMPUTING_IDS, CURRENT_EXEC_EMAIL_LIST, \
    CURRENT_AND_PAST_MINUS_1_EXEC_EMAIL_LIST
from csss.views.privilege_validation.list_of_officer_details_from_past_specified_terms import get_relevant_terms


def create_context_for_current_email_mappings_html(context, officer_emaillist_and_position_mappings):
    context[EMAIL_LIST_MAPPINGS] = []
    officers = Officer.objects.all().filter(
        elected_term__in=Term.objects.all().filter(
            term_number__in=get_relevant_terms()
        )
    ).order_by('-start_date')
    current_executive_officers = []
    current_and_past_minus_1_executive_officers = [CURRENT_EXEC_EMAIL_LIST]
    email_lists = []
    for position in officer_emaillist_and_position_mappings.exclude(email='NA').order_by('position_index'):
        if position.email not in email_lists:
            email_lists.append(position.email)
    for email_list in email_lists:
        current_officers_to_show = []
        current_and_previous_officers_to_show = []
        for applicable_position in officer_emaillist_and_position_mappings.filter(email=email_list):
            officers_to_show = officers.filter(
                position_name=applicable_position.position_name
            ).order_by('-start_date')
            sfuids_of_officers_to_show = []
            for officer_to_show in officers_to_show:
                if officer_to_show.sfu_computing_id not in sfuids_of_officers_to_show:
                    sfuids_of_officers_to_show.append(officer_to_show.sfu_computing_id)
            current_officers_to_show.extend(sfuids_of_officers_to_show[:1])
            current_and_previous_officers_to_show.append(email_list)
            current_and_previous_officers_to_show.extend(sfuids_of_officers_to_show[1:2])
            if applicable_position.executive_officer:
                current_executive_officers.append(email_list)
                if '-current' in email_list:
                    current_and_past_minus_1_executive_officers.append(email_list.replace("-current", ""))

        context[EMAIL_LIST_MAPPINGS].append({
            SFU_EMAIL_LIST: email_list,
            SFU_COMPUTING_IDS: list(set(current_officers_to_show))
        })
        if '-current' in email_list:
            context[EMAIL_LIST_MAPPINGS].append({
                SFU_EMAIL_LIST: email_list.replace("-current", ""),
                SFU_COMPUTING_IDS: list(set(current_and_previous_officers_to_show))
            })

    context[EMAIL_LIST_MAPPINGS].append({
        SFU_EMAIL_LIST: CURRENT_EXEC_EMAIL_LIST,
        SFU_COMPUTING_IDS: list(set(current_executive_officers))
    })
    context[EMAIL_LIST_MAPPINGS].append({
        SFU_EMAIL_LIST: CURRENT_AND_PAST_MINUS_1_EXEC_EMAIL_LIST,
        SFU_COMPUTING_IDS: list(set(current_and_past_minus_1_executive_officers))
    })
