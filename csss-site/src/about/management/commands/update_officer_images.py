import datetime

from django.core.management import BaseCommand

from csss.setup_logger import date_timezone, Loggers
from about.views.commands.update_officer_images import update_officer_images as update_officer_images_job

SERVICE_NAME = "update_officer_images"


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
        current_date = datetime.datetime.now(date_timezone)
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        logger.info(options)
        update_officer_images_job(SERVICE_NAME,download=options['download'])
        Loggers.remove_logger(SERVICE_NAME, current_date)
