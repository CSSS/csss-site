import requests

from csss.settings import discord_header


def get_user_nickname(guild_id, user_id):
    """
    Attempt to obtain the nickname of the user for a specific guild

    Keyword Argument
    guild_id -- the ID of the guild for the nickname
    user_id -- the ID of the user whose nickname to obtain for the specified guild

    Return
    bool -- True if discord API call was successful and false otherwise
    str -- the nickname [if the user has a nickname, otherwise, just their username], the error
     from the API call otherwise
    """
    response = requests.get(
        f"https://discord.com/api/guilds/{guild_id}/members/{user_id}", headers=discord_header
    )
    if response.status_code == 200:
        nickname = response.json()['nick']
        return True, nickname if nickname else response.json()['user']['username']
    else:
        return False, f"Unable to interact with Discord API due to error \"{response.reason}\""
