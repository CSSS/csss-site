import datetime
import logging

from django.shortcuts import render

from about.models import Officer, Term
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from csss.views_helper import create_main_context, get_current_term, get_previous_term

logger = logging.getLogger('csss_site')


def who_we_are(request):
    """
    Show the page what details what CSSS is about
    """
    return render(request, 'about/who_we_are.html', create_main_context(request, TAB_STRING))


def list_of_current_officers(request):
    """
    Lists all current CSSS Officers
    """
    context = create_main_context(request, TAB_STRING)

    context.update({
        'officers': list(
            map(
                fix_time_for_officer,
                Officer.objects.all().filter(elected_term=get_current_term()).order_by(
                    'elected_term__term_number', 'position_index', '-start_date'
                )
            )
        ),
        'term_active': get_current_term(),
        'terms': [Term.objects.all().order_by('-term_number')[0]],
    })
    return render(request, 'about/list_of_officers.html', context)


def list_of_past_officers(request):
    """
    Lists all past CSSS Officers
    """
    context = create_main_context(request, TAB_STRING)

    context.update({
        'officers': list(
            map(
                fix_time_for_officer,
                Officer.objects.all().exclude(
                    elected_term=get_current_term()).order_by(
                    'elected_term__term_number', 'position_index', '-start_date'
                )
            )
        ),
        'term_active': get_previous_term(),
        'terms': Term.objects.all().exclude(term_number=get_current_term()).order_by('-term_number'),
    })
    return render(request, 'about/list_of_officers.html', context)


def fix_time_for_officer(officer):
    """
    fix the start date for the officers before showing them to the user
    The start date needs its time component removed

    Keyword Argument
    officer -- the officer whose start date needs to be changed

    Return
    officer -- the officer whose start date's time was removed
    """
    officer.start_date = datetime.datetime.strftime(officer.start_date, "%d %b %Y")
    return officer
