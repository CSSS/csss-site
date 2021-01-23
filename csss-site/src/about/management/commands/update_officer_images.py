import logging

from django.core.management import BaseCommand

from about.models import Officer
from about.views.officer_position_and_github_mapping.officer_management_helper import get_officer_image_path

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "check to see if the officer's pictures need to be updated"

    def handle(self, *args, **options):
        logger.info(options)
        for officer in Officer.objects.all().filter():
            fix_image_for_officer(officer)


def fix_image_for_officer(officer):
    """
    checks to see if the officer's picture has been uploaded. if it has been, it will set the officer image
    to the uploaded photo

    Keyword Argument
    officer -- officer whose image needs to be changed
    """
    officer.image = get_officer_image_path(officer.elected_term, officer.name)
    logger.info("[about/update_officer_images.py fix_image_for_officer()] "
                f"officer_image_path = {officer.image}")
    officer.save()
