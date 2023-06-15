from django.shortcuts import render

from about.models import Officer, Term
from about.views.Constants import TAB_STRING
from csss.views.context_creation.create_main_context import create_main_context
from csss.views_helper import get_current_term, get_previous_term


def list_of_past_officers(request):
    """
    Lists all past CSSS Officers
    """
    context = create_main_context(request, TAB_STRING)
    officer_map = {}
    show_all_officers = context['root_user'] or context['officer_in_past_5_terms']
    officers = Officer.objects.all().exclude(
        elected_term__term_number__gte=get_current_term()).order_by(
        'elected_term__term_number', 'position_index', '-start_date'
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
        'term_active': get_previous_term(),
        'terms': Term.objects.all().exclude(term_number__gte=get_current_term()).order_by('-term_number'),
    })
    return render(request, 'about/list_of_officers.html', context)
