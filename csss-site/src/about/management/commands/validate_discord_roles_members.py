from django.core.management import BaseCommand

from about.views.commands.validate_discord_roles_members import validate_discord_roles_members


class Command(BaseCommand):
    help = "Ensure that the Discord Roles associated with the Officers have valid members"

    def handle(self, *args, **options):
        validate_discord_roles_members.run_job()
