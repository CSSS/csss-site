import json

import requests
from django.conf import settings

from csss.settings import discord_header


def get_role_dictionary():
    """
    Creates a dictionary where the key is the role_id and the value is the role object

    Return
    bool -- True or false depending on if there was an issue with talking to the discord API
    error_message -- the message received alongside the error
    role_id__role -- a dictionary where the key is the role_id and the value is the corresponding role object
    """
    base_url = f"https://discord.com/api/guilds/{settings.GUILD_ID}/roles"
    resp = requests.get(base_url, headers=discord_header)
    role_id__role = None
    if resp.status_code == 200:
        role_id__role = {
            role['id']: role
            for role in json.loads(resp.text)
        }
        return True, None, role_id__role
    else:
        return False, "Unable to get a dictionary of the roles", role_id__role
