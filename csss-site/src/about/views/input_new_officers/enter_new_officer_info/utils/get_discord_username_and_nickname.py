import json

import requests
from django.conf import settings

from csss.settings import discord_header


def get_discord_username_and_nickname(discord_id):
    """
    get the discord username and nickname for user with the given discord ID

    Keyword Argument
    discord_id -- ID of the discord user whose username and nicknames to get

    Return
    bool -- true or false depending on if the discord_id belongs to a user whose info can be extracted
    error_message -- returns the error message from the discord API, if there was any. otherwise None
    discord_username --  the discord username for the user with the given discord ID
    discord_nickname -- the discord nickname for the user with the given discord ID
    """
    resp = requests.get(
        f"https://discord.com/api/guilds/{settings.GUILD_ID}/members/{discord_id}",
        headers=discord_header,
    )
    if resp.status_code != 200:
        if 'user_id' not in json.loads(resp.text):
            message = (
                f"Could not locate the discord user for ID {discord_id} due to "
                f"error: '{json.loads(resp.text)['message']}'"
            )
        else:
            texts = "<br>".join(json.loads(resp.text)['user_id'])
            message = (
                f"{discord_id} does not seem to be a valid Discord ID. "
                f"<br>Received a response of {resp.reason}: {texts} from discord API"
            )
        return False, message, None, None
    user_info = json.loads(resp.text)
    return True, None, user_info['user']['username'], user_info['nick']
