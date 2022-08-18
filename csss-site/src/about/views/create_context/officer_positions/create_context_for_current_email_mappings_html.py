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
    current_and_past_minus_1_officers = [CURRENT_EXEC_EMAIL_LIST]
    current_officers = []
    for officer_emaillist_and_position_mapping in officer_emaillist_and_position_mappings:
        if officer_emaillist_and_position_mapping.email != "NA":
            officers_to_show = officers.filter(
                position_name=officer_emaillist_and_position_mapping.position_name
            ).order_by('-start_date')[:2]
            officers_to_show = list(set([officer_to_show.sfu_computing_id for officer_to_show in officers_to_show]))
            if officer_emaillist_and_position_mapping.executive_officer:
                current_and_past_minus_1_officers.extend(officers_to_show[1:3])
                current_officers.extend(officers_to_show[:1])
            context[EMAIL_LIST_MAPPINGS].append({
                SFU_EMAIL_LIST: officer_emaillist_and_position_mapping.email,
                SFU_COMPUTING_IDS: officers_to_show
            })
    current_officers = list(set(current_officers))
    current_and_past_minus_1_officers = list(set(current_and_past_minus_1_officers))
    context[EMAIL_LIST_MAPPINGS].append({
        SFU_EMAIL_LIST: CURRENT_EXEC_EMAIL_LIST,
        SFU_COMPUTING_IDS: current_officers
    })
    context[EMAIL_LIST_MAPPINGS].append({
        SFU_EMAIL_LIST: CURRENT_AND_PAST_MINUS_1_EXEC_EMAIL_LIST,
        SFU_COMPUTING_IDS: current_and_past_minus_1_officers
    })
