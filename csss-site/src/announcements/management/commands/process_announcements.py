from django.core.management.base import BaseCommand

from announcements.views.commands.process_announcements import process_announcements
from csss.setup_logger import get_or_setup_logger


class Command(BaseCommand):
    help = "process the latest new emails and manual announcements and determines which to display"

    def add_arguments(self, parser):
        parser.add_argument(
            '--poll_email',
            action='store_true',
            default=False,
            help="pull the latest emails from gmail"
        )

    def handle(self, *args, **options):
        logger = get_or_setup_logger(logger_name="process_announcements")
        logger.info(options)
        process_announcements.run_job(poll_email=options['poll_email'])
