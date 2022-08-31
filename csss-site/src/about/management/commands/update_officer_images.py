import logging
import os

from django.conf import settings
from django.core.management import BaseCommand

from about.models import Officer
from about.views.utils.get_officer_image_path import get_officer_image_path

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "check to see if the officer's pictures need to be updated"

    def add_arguments(self, parser):
        parser.add_argument(
            '--download',
            action='store_true',
            default=False,
            help="pull the latest exec-photos from the staging server"
        )

    def handle(self, *args, **options):
        logger.info(options)
        update_officer_images(options['download'])


def update_officer_images(download=False):
    if download:
        os.system(
            "rm -fr about/static/about_static/exec-photos || true; "
            f"wget -r -X '*' --no-host-directories {settings.STAGING_SERVER}exec-photos/ -R "
            "'*html*' -P about/static/about_static/ || true"
        )
    for officer in Officer.objects.all().filter():
        _fix_image_for_officer(officer)


def _fix_image_for_officer(officer):
    """
    checks to see if the officer's picture has been uploaded. if it has been, it will set the officer image
    to the uploaded photo

    Keyword Argument
    officer -- officer whose image needs to be changed
    """
    officer.image = get_officer_image_path(officer.elected_term, officer.full_name)
    logger.info("[about/update_officer_images.py fix_image_for_officer()] "
                f"officer_image_path = {officer.image}")
    officer.save()
