from django.core.management import BaseCommand

from about.views.commands.update_officer_images import update_officer_images
from csss.setup_logger import Loggers

SERVICE_NAME = 'update_officer_images'


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
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        logger.info(options)
        update_officer_images(download=options['download'])
        Loggers.remove_logger(SERVICE_NAME)
