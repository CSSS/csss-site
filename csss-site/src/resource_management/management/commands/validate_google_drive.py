import logging

from django.core.management.base import BaseCommand

from resource_management.views.commands.validate_google_drive import run_job as validate_google_drive_validation_job

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "validates the access for the google drive"

    def handle(self, *args, **options):
        logger.info(options)
        logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                    "to google drive")
        validate_google_drive_validation_job()
