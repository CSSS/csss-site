import datetime
import logging
import os

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import render

from about.models import Officer, Term
from about.views.officer_management_helper import TAB_STRING
from csss.settings import ENVIRONMENT, STATIC_ROOT
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
    # path_prefix = "about_static/exec-photos/" \
    #     if ENVIRONMENT == "PRODUCTION" or ENVIRONMENT == "STAGING" else ""
    # logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] path_prefix = {path_prefix}")
    # logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] officer.image = {officer.image}")
    # officer.image = f"{path_prefix}{officer.image}"

    # if ENVIRONMENT == "LOCALHOST":
    #     officer.image = finders.find(officer.image)
    # else:
    #     absolute_path = finders.find(officer.image)
    #     file_exists = staticfiles_storage.exists(absolute_path)
    #     if file_exists
    #     # officer.image = static(officer.image)
    logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
                f"officer_image_path = {officer.image}")
    # if officer.image is None:
    #     officer.image = f"{path_prefix}stockPhoto.jpg"
    # else:
    #     if not os.path.isfile(officer.image) and ENVIRONMENT == "LOCALHOST":
    #         officer.image = f"{path_prefix}stockPhoto.jpg"

    if ENVIRONMENT == "LOCALHOST":
        officer.image = f"{officer.image}"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] officer.image = {officer.image}")
        officer.image = finders.find(officer.image)
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] officer.image = {officer.image}")
        if not os.path.isfile(officer.image):
            officer.image = "stockPhoto.jpg"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] officer.image = {officer.image}")
    else:
        path_prefix = "about_static/exec-photos/"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] path_prefix = {path_prefix}")
        officer.image = f"{path_prefix}{officer.image}"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] officer.image = {officer.image}")
        absolute_path = f"{STATIC_ROOT}{officer.image}"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] absolute_path = {absolute_path}")
        file_exists = os.path.isfile(absolute_path)
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] file_exists = {file_exists}")
        if not file_exists:
            officer.image = f"{path_prefix}stockPhoto.jpg"
        logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
                    f"officer.image = {officer.image}")
        # else:
        # officer.image = f"{path_prefix}stockPhoto.jpg"
        # logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
        #             f"officer.image = {officer.image}")
        # logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
        #             f"absolute_path = {absolute_path}")
        # file_exists = staticfiles_storage.exists(absolute_path)
        # logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
        #             f"file_exists = {file_exists}")

    officer.start_date = datetime.datetime.strftime(officer.start_date, "%d %b %Y")
    return officer
