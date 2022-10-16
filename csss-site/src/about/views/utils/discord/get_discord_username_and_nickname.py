import json
from time import sleep

import requests
from django.conf import settings

from csss.settings import discord_header
from csss.setup_logger import get_logger

logger = get_logger()


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
    while resp.status_code == 429:
        logger.info(
            "[about/get_discord_username_and_nickname.py()] going to bed before asking again since "
            f"I got the error of {resp.reason} with status_code of {resp.status_code}"
        )
        sleep(10)
        resp = requests.get(
            f"https://discord.com/api/guilds/{settings.GUILD_ID}/members/{discord_id}",
            headers=discord_header,
        )
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}' with status code {resp.status_code}", None, None
    user_info = json.loads(resp.text)
    return True, None, user_info['user']['username'], user_info['nick']
