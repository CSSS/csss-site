import logging

from django.core.management.base import BaseCommand

from resource_management.views.resource_views import validate_google_drive, validate_github, validate_sfu_gitlab

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "validates the access for the google drive"

    def add_arguments(self, parser):
        parser.add_argument(
            '--google_drive',
            action="store_true",
            default=False,
            help="validates the access to the SFU CSSS Google Drive"
        )
        parser.add_argument(
            '--github',
            action="store_true",
            default=False,
            help="validates the access to the SFU CSSS GitHub "
        )
        parser.add_argument(
            "--gitlab",
            action="store_true",
            default=False,
            help="validate the access to the SFU Gitlab CSSS team"
        )

    def handle(self, *args, **options):
        logger.info(options)
        if options['google_drive']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to google drive")
            validate_google_drive()
        if options['github']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to Github")
            validate_github()
        if options['gitlab']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to the SFU Gitlab")
            validate_sfu_gitlab()



