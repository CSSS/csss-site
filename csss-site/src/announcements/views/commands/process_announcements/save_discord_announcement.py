from django.conf import settings

from announcements.models import DiscordAnnouncement
from announcements.views.commands.process_announcements.get_user_nickname import get_user_nickname
from csss.setup_logger import Loggers


def save_discord_announcement(indx, number_of_messages, message, guild_members):
    """
    Saves the specified message

    Keyword Argument
    indx -- the index of the current message
    number_of_messages -- the number of messages being processed
    message -- the message being processed
    guild_members -- a dict that contains the nicknames/usernames of a user for the value with the user_id
     for the key
    """
    from announcements.management.commands.process_announcements import SERVICE_NAME
    logger = Loggers.get_logger(logger_name=SERVICE_NAME)
    if message['author']['id'] in guild_members:
        author = guild_members[message['author']['id']]
    else:
        success, nickname = get_user_nickname(settings.GUILD_ID, message['author']['id'])
        if success:
            author = nickname
            guild_members[message['author']['id']] = author
        else:
            author = message['author']['username']
    DiscordAnnouncement(
        author=author,
        author_id=message['author']['id'],
        content=message['content'],
        date=DiscordAnnouncement.get_date_for_message(message['timestamp']),
        channel_id=message['channel_id'],
        message_id=message['id']
    ).save()
    logger.info(f"[process_announcements save_discord_announcement()] saved announcement {indx}/{number_of_messages}")
