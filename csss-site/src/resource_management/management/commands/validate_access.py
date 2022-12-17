from django.core.management.base import BaseCommand

from csss.setup_logger import Loggers
from resource_management.views.resource_views import validate_google_drive, validate_github


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

    def handle(self, *args, **options):
        logger = Loggers.get_logger(logger_name="admin_commands_validate_access")
        logger.info(options)
        if options['google_drive']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to google drive")
            validate_google_drive()
        if options['github']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to Github")
            validate_github()
        Loggers.remove_logger(logger_name="admin_commands_validate_access")