from django.core.management import BaseCommand

from about.views.commands import update_officer_images
from csss.setup_logger import get_logger


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
        logger = get_logger()
        logger.info(options)
        update_officer_images.run_job(download=options['download'])
