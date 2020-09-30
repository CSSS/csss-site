import logging
import os

from django.contrib.staticfiles import finders
from django.core.management import BaseCommand

from about.models import Officer
from about.views.officer_management_helper import get_officer_image_path
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
        officer.image = get_officer_image_path(officer.elected_term, officer.name)
    logger.info("[about/officer_management.py fix_time_and_image_for_officer()] "
                f"officer.image = {officer.image}")
    officer.save()
