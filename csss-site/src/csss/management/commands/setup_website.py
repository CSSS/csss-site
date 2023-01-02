import logging

from django.core.management import BaseCommand

from about.views.commands.update_officer_images import run_job
from announcements.management.commands.create_attachments import download_or_create_announcement_attachments

logger = logging.getLogger('csss_site')


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
        logger.info(options)
        download_or_create_announcement_attachments(options['download__attachments'])
        run_job(download=options['download__officer_images'])
