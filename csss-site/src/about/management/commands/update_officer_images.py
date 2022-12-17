from django.core.management import BaseCommand

from about.views.commands.update_officer_images import run_job


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
        run_job(download=options['download'], use_cron_logger=False)
