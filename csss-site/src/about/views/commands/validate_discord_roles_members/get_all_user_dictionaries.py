import json

import requests
from django.conf import settings

from csss.settings import discord_header


def get_all_user_dictionaries():
    """
    Creates a dictionary where about the roles and the members that are a part of them

    Return
    bool -- True or false depending on if there was an issue with talking to the discord API
    error_message -- the message received alongside the error
    role_id__list_of_users -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    user_id__user_obj -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    """
    role_id__list_of_users = {}
    after = None
    first = True
    user_id__user_obj = {}
    while after is not None or first:
        first = False
        base_url = f"https://discord.com/api/guilds/{settings.GUILD_ID}/members?limit=1000"
        if after is not None:
            url = f"{base_url}&after={after}"
        else:
            url = base_url
        resp = requests.get(url, headers=discord_header)
        if resp.status_code == 200:
            users = json.loads(resp.text)
            if len(users) > 0:
                for user in users:
                    user_id__user_obj[user['user']['id']] = user
                    for role_id in user['roles']:
                        if role_id in role_id__list_of_users:
                            role_id__list_of_users[role_id].append(user)
                        else:
                            role_id__list_of_users[role_id] = [user]
                after = users[len(users) - 1]['user']['id']
            else:
                after = None
        else:
            return (
                False,
                (f"Unable to get the users with the following url [{url}] "
                 f"due to error {json.loads(resp.text)['message']}"
                 ),
                role_id__list_of_users, user_id__user_obj
            )

    return True, None, role_id__list_of_users, user_id__user_obj
