from django.core.management import BaseCommand

from about.management.commands.update_officer_images import update_officer_images
from announcements.management.commands.create_attachments import download_or_create_announcement_attachments
from csss.setup_logger import get_logger


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
        logger = get_logger()
        logger.info(options)
        download_or_create_announcement_attachments(options['download__attachments'])
        update_officer_images(options['download__officer_images'])
