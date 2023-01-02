from django.core.management import BaseCommand

from about.views.commands.update_discord_details import run_job


class Command(BaseCommand):
    help = "get the latest discord name and nicknames for the officers"

    def handle(self, *args, **options):
        run_job()
