import logging
import os

from django.conf.global_settings import STATIC_ROOT
from django.contrib.staticfiles import finders
from django.core.management import BaseCommand

from about.models import Officer
from csss.settings import ENVIRONMENT

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "check to see if the officer's pictures need to be updated"

    def handle(self, *args, **options):
        logger.info(options)
        for officer in Officer.objects.all().filter():
            fix_image_for_officer(officer)


def fix_image_for_officer(officer):
    """
    Fix the officer's photo before showing to user
    the photo needs to be check to see if the officer's pic is valid and then if the stock photo is existent

    Keyword Argument
    officer -- officer whose image needs to be changed

    Return
    officer -- the officer whose image was checked
    """
    logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
                f"officer_image_path = {officer.image}")

    if ENVIRONMENT == "LOCALHOST":
        full_path = finders.find(officer.image)
        logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
                    f"full_path = {full_path}")
        if full_path is None or not os.path.isfile(full_path):
            officer.image = "stockPhoto.jpg"
    else:
        path_prefix = "about_static/exec-photos/"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] "
                    f"path_prefix = {path_prefix}")
        officer.image = f"{path_prefix}{officer.image}"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] "
                    f"officer.image = {officer.image}")
        absolute_path = f"{STATIC_ROOT}{officer.image}"
        logger.info(f"[about/officer_management.py fix_time_and_image_for_officer()] "
                    f"absolute_path = {absolute_path}")
        if not os.path.isfile(absolute_path):
            officer.image = f"{path_prefix}stockPhoto.jpg"
    logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
                f"officer.image = {officer.image}")
    officer.save()
