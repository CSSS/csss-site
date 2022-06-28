import logging

from django.core.management import BaseCommand

from about.models import NewOfficer
from about.views.input_new_officers.discord_dms.dm_new_officers_on_discord import dm_new_officers_on_discord

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "DMs all the New officers to ask them for their info"

    def handle(self, *args, **options):
        logger.info(options)
        [
            dm_new_officers_on_discord(new_officer.full_name, new_officer.discord_id)
            for new_officer in NewOfficer.objects.all()
        ]
