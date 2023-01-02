import logging

from django.core.management import BaseCommand

from about.views.commands.validate_discord_roles_members.validate_discord_roles_members import run_job

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "Ensure that the Discord Roles associated with the Officers have valid members"

    def handle(self, *args, **options):
        run_job()
