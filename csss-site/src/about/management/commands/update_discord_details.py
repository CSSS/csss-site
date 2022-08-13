import logging

from django.core.management import BaseCommand

from about.models import Officer
from about.views.utils.discord.get_discord_username_and_nickname import get_discord_username_and_nickname

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "get the latest discord name and nicknames for the officers"

    def handle(self, *args, **options):
        officers = Officer.objects.all().exclude(discord_id="NA")
        officers_discord_ids = list(set(list(officers.values_list('discord_id', flat=True))))
        discord_info_maps = {}
        max_retries = 5
        for officers_discord_id in officers_discord_ids:
            success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(
                officers_discord_id
            )
            retries = 0
            while not success and retries < max_retries:
                success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(
                    officers_discord_id
                )
                retries += 1
            officer = officers.filter(discord_id=officers_discord_id).first()
            if success:
                logger.info(
                    f"[about/update_discord_details.py()] the nickname or username for {officer.full_name} "
                    f"was update since last time"
                )
                discord_info_maps[officer.sfu_computing_id] = {
                    'officers_discord_id': officers_discord_id,
                    'discord_username': discord_username,
                    'discord_nickname': discord_nickname
                }
            else:
                logger.info(
                    f"[about/update_discord_details.py()] unable to get the discord username and nickname for "
                    f"{officer.full_name} due to error {error_message}"
                )
        officers_to_change = officers.filter(sfu_computing_id__in=list(discord_info_maps.keys()))

        for officer in officers_to_change:
            officer.discord_id = discord_info_maps[officer.sfu_computing_id]['officers_discord_id']
            officer.discord_username = discord_info_maps[officer.sfu_computing_id]['discord_username']
            officer.discord_nickname = discord_info_maps[officer.sfu_computing_id]['discord_nickname']
        Officer.objects.bulk_update(officers_to_change, ['discord_id', 'discord_username', 'discord_nickname'])
