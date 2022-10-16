from django.core.management import BaseCommand

from about.views.commands import update_discord_details


class Command(BaseCommand):
    help = "get the latest discord name and nicknames for the officers"

    def handle(self, *args, **options):
        update_discord_details.run_job()
