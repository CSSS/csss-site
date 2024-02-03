import json

import requests


from announcements.models import DiscordAnnouncement
from announcements.views.commands.process_announcements.save_discord_announcement import save_discord_announcement
from csss.settings import discord_header
from csss.setup_logger import Loggers
from csss.views.pstdatetime import pstdatetime


def get_latest_discord_announcements(channel_id):
    """
    Saves the latest messages in the specific channel to DiscordAnnouncement

    Keyword Arguments
    channel_id -- the id of the channel to pull the messages from
    """
    from announcements.management.commands.process_announcements import SERVICE_NAME
    logger = Loggers.get_logger(logger_name=SERVICE_NAME)
    latest_discord_announcement = DiscordAnnouncement.objects.all().filter(channel_id=channel_id).order_by(
        '-date').first()
    url = f"https://discord.com/api/channels/{channel_id}/messages"
    if latest_discord_announcement:
        url += f"?after={latest_discord_announcement.message_id}"

    response = requests.get(url, headers=discord_header)
    if response.status_code == 200:
        messages = json.loads(response.content)
        current_messages = list(
            DiscordAnnouncement.objects.all().filter(channel_id=channel_id).values_list('message_id', flat=True)
        )
        indx = 0
        guild_members = {}
        new_message = messages[indx]['id'] not in current_messages

        def message_to_process(pulled_message, unprocessed_message):
            switch_to_discord_date = pstdatetime.create_pst_time(2024, 2, 1)
            return (
                DiscordAnnouncement.get_date_for_message(pulled_message['timestamp']) >= switch_to_discord_date and
                unprocessed_message
            )
        while message_to_process(messages[indx], new_message):
            message = messages[indx]
            save_discord_announcement(indx, len(messages), message, guild_members)
            indx += 1
            new_message = messages[indx]['id'] not in current_messages
        logger.info("[process_announcements get_latest_discord_announcements()] done processing announcements")
        return True, None
    else:
        return False, f"Unable to interact with Discord API due to error \"{response.reason}\""
