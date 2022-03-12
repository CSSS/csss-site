import json

import requests
from django.conf import settings


def validate_discord_id(discord_id):
    headers = {
        "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    # snowflake = None
    # users = []
    # last_size = 1
    # while last_size != users:
    #     last_size = len(users)
    #     url = "https://discord.com/api/guilds/228761314644852736/members?limit=1000"
    #     if snowflake is not None:
    #         url += f"&after={snowflake}"
    #     resp = requests.get(
    #         url,
    #         headers=headers
    #         # ,data=json.dumps(
    #         #     {"recipient_id": discord_id}
    #         # )
    #     )
    #     users.extend([user for user in json.loads(resp.text)])
    #     snowflake = sorted([user['user']['id'] for user in json.loads(resp.text)], reverse=True)[0]
    resp = requests.post(
        "https://discord.com/api/users/@me/channels",
        headers=headers,
        data=json.dumps(
            {"recipient_id": discord_id}
        )
    )
    # resp = requests.get(
    #     f"https://discord.com/api/guilds/228761314644852736/members/{discord_id}",
    #     headers=headers
    # )
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}'"

    # requests.post(
    #     f"https://discord.com/api/channels/{resp.id}/messages", headers=headers,
    #     data={
    #         "content": "hi"
    #     }
    # )
    return True, None
