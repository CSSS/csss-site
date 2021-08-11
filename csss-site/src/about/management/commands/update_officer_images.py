import logging
import os

from django.core.management import BaseCommand

from about.models import Officer
from about.views.officer_position_and_github_mapping.officer_management_helper import get_officer_image_path

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "check to see if the officer's pictures need to be updated"

    def add_arguments(self, parser):
        parser.add_argument(
            '--poll_email',
            action='store_true',
            default=False,
            help="pull the latest exec-photos from the staging server"
        )

    def handle(self, *args, **options):
        logger.info(options)
        if options['download']:
            os.system(
                "rm -fr about/static/about_static/exec-photos || true; "
                "wget -r --no-host-directories https://dev.sfucsss.org/exec-photos/ -R "
                "'*html*' -P about/static/about_static/ || true"
            )
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
