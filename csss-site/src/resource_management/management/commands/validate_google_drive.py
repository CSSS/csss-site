import datetime

from django.core.management.base import BaseCommand

from csss.setup_logger import Loggers, date_timezone
from resource_management.views.commands.validate_google_drive import run_job as validate_google_drive_validation_job

SERVICE_NAME = "validate_google_drive"


class Command(BaseCommand):
    help = "validates the access for the google drive"

    def handle(self, *args, **options):
        current_date = datetime.datetime.now(date_timezone)
        logger = Loggers.get_logger(logger_name=SERVICE_NAME, current_date=current_date)
        logger.info(options)
        logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                    "to google drive")
        validate_google_drive_validation_job()
        Loggers.remove_logger(SERVICE_NAME, current_date)
