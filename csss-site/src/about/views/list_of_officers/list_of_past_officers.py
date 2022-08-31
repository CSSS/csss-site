from django.shortcuts import render

from about.models import Officer, Term
from about.views.Constants import TAB_STRING
from about.views.list_of_officers.fix_start_date_and_bio_for_officer import fix_start_date_and_bio_for_officer
from csss.views.context_creation.create_main_context import create_main_context
from csss.views_helper import get_current_term, get_previous_term


def list_of_past_officers(request):
    """
    Lists all past CSSS Officers
    """
    context = create_main_context(request, TAB_STRING)

    context.update({
        'officers': list(
            map(
                fix_start_date_and_bio_for_officer,
                Officer.objects.all().exclude(
                    elected_term__term_number__gte=get_current_term()).order_by(
                    'elected_term__term_number', 'position_index', '-start_date'
                )
            )
        ),
        'term_active': get_previous_term(),
        'terms': Term.objects.all().exclude(term_number__gte=get_current_term()).order_by('-term_number'),
    })
    return render(request, 'about/list_of_officers.html', context)
