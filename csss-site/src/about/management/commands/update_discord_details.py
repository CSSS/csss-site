from django.core.management import BaseCommand

from about.models import Officer
from about.views.utils.discord.get_discord_username_and_nickname import get_discord_username_and_nickname


class Command(BaseCommand):
    help = "get the latest discord name and nicknames for the officers"

    def handle(self, *args, **options):
        officers = Officer.objects.all().exclude(discord_id="NA")
        officers_discord_ids = list(set(list(officers.values_list('discord_id', flat=True))))
        discord_info_maps = {}
        for officers_discord_id in officers_discord_ids:
            success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(
                officers_discord_id
            )
            if success:
                officer = officers.filter(discord_id=officers_discord_id).first()
                if officer.discord_nickname != discord_nickname or officer.discord_username != discord_username:
                    discord_info_maps[officers_discord_id] = {
                        'discord_username': discord_username,
                        'discord_nickname': discord_nickname
                    }
        officers_to_change = officers.filter(discord_id__in=discord_info_maps.keys())

        for officer in officers_to_change:
            officer.discord_username = discord_info_maps[officer.discord_id]['discord_username']
            officer.discord_nickname = discord_info_maps[officer.discord_id]['discord_nickname']
        Officer.objects.bulk_update(officers_to_change, ['discord_username', 'discord_nickname'])
