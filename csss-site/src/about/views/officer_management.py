import datetime
import logging
import os

from django.conf import settings
from django.shortcuts import render

from about.models import Officer, Term
from about.views.officer_management_helper import TAB_STRING
from csss.views_helper import create_main_context, get_current_active_term

logger = logging.getLogger('csss_site')


def who_we_are(request):
    """
    Show the page what details what CSSS is about
    """
    return render(request, 'about/who_we_are.html', create_main_context(request, TAB_STRING))


def list_of_officers(request):
    """
    Lists all current and past CSSS Officers
    """
    context = create_main_context(request, TAB_STRING)

    context.update({
        'officers': list(
            map(
                remove_time_from_start_date,
                Officer.objects.all().filter().order_by('elected_term__term_number', 'term_position_number',
                                                        '-start_date')
            )
        ),
        'term_active': get_current_active_term(),
        'terms': Term.objects.all().order_by('-term_number'),
    })
    return render(request, 'about/list_of_officers.html', context)


def remove_time_from_start_date(officer):
    """
    removes the time from the start date for officer before showing it to front-end user

    Keyword Argument
    officer -- officer whose start date needs needs its time removed

    Return
    officer -- the officer whose start date's time was removed
    """
    officer.start_date = datetime.datetime.strftime(officer.start_date, "%d %b %Y")
    if not os.path.isfile(officer.image):
        if os.path.isfile(f"{settings.OFFICER_PHOTOS_PATH}/stockPhoto.jpg"):
            officer.image = os.path.isfile(f"{settings.OFFICER_PHOTOS_PATH}/stockPhoto.jpg")
        else:
            officer.image = "No valid path detected"
    return officer
