from django.core.management import BaseCommand

from about.views.commands.update_officer_images import run_job
from announcements.management.commands.create_attachments import download_or_create_announcement_attachments
from csss.setup_logger import Loggers


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
        logger = Loggers.get_logger(logger_name="setup_website")
        logger.info(options)
        download_or_create_announcement_attachments(options['download__attachments'])
        run_job(download=options['download'], use_cron_logger=False)
        Loggers.remove_logger(logger_name="setup_website")
