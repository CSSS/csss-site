import datetime

from django.core.management import BaseCommand

from about.views.commands.update_officer_images import update_officer_images
from announcements.management.commands.create_attachments import download_or_create_announcement_attachments
from csss.setup_logger import Loggers, date_timezone

SERVICE_NAME = "setup_website"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--download__attachments',
            action='store_true',
            default=False,
            help="pull the latest email attachments from staging server"
        )
        parser.add_argument(
            '--download__officer_images',
            action='store_true',
            default=False,
            help="pull the latest exec-photos from the staging server"
        )

    def handle(self, *args, **options):
        current_date = datetime.datetime.now(date_timezone)
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        logger.info(options)
        download_or_create_announcement_attachments(options['download__attachments'])
        update_officer_images(SERVICE_NAME, download=options['download__officer_images'])
        Loggers.remove_logger(SERVICE_NAME, current_date)
