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
                fix_time_and_image_for_officer,
                Officer.objects.all().filter().order_by('elected_term__term_number', 'term_position_number',
                                                        '-start_date')
            )
        ),
        'term_active': get_current_active_term(),
        'terms': Term.objects.all().order_by('-term_number'),
    })
    return render(request, 'about/list_of_officers.html', context)


def fix_time_and_image_for_officer(officer):
    """
    Fix the start date and officer's photo before showing to user
    The start date needs its time component removed
    the photo needs to be check to see if the officer's pic is valid and then if the stock photo is existent

    Keyword Argument
    officer -- officer whose start date and image needs to be changed

    Return
    officer -- the officer whose start date's time was removed and image was checked
    """
    officer.start_date = datetime.datetime.strftime(officer.start_date, "%d %b %Y")
    existent_stock_photo = os.path.isfile(f"{settings.OFFICER_PHOTOS_PATH}/stockPhoto.jpg")
    stock_photo_path = f"{settings.OFFICER_PHOTOS_PATH}/stockPhoto.jpg" \
        if existent_stock_photo else "No_valid_path_detected"
    if not os.path.isfile(officer.image):
        officer.image = stock_photo_path
    return officer
