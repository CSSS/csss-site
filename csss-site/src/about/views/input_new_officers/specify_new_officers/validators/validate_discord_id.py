import json

import requests
from django.conf import settings

from csss.settings import discord_header


def validate_discord_id(discord_id):
    """
    Ensures that the given discord_id belongs to a valid discord username that the website can DM

    Keyword Argument
    discord_id -- ID of the discord user to validate

    Return
    bool -- true or false depending on if the discord_id belongs to a user that can be DMed
    error_message -- returns the error message from the discord API, if there was any. otherwise None
    """
    staging = settings.ENVIRONMENT == "STAGING" and discord_header['Authorization'] == "Bot DISCORD_BOT_TOKEN"
    if not staging:
        resp = requests.post(
            "https://discord.com/api/users/@me/channels",
            headers=discord_header,
            data=json.dumps(
                {"recipient_id": discord_id}
            )
        )
        if resp.status_code != 200 and discord_header:
            return False, f"Encountered error message of '{resp.reason}' when validating Discord ID {discord_id}"
    return True, None
