import json
import os

import requests
from django.conf import settings


def dm_new_officers_on_discord(full_name, recipient_id):
    response = requests.post(
        "https://discord.com/api/users/@me/channels",
        data=json.dumps({
            "recipient_id": recipient_id
        }),
        headers={
            "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    if response.status_code:
        requests.post(
            f"https://discord.com/api/channels/{response.json()['id']}/messages",
            data=json.dumps(
                {
                    "tts": False,
                    "embeds": [{
                        "title": f"Enter Information",
                        "description": (
                            f"Hello {full_name},\n\n"
                            f"[Click on this link to complete the process of becoming a new officer for the CSSS]"
                            f"(http://127.0.0.1:8000/login?next=/about/enter_info)"
                        )
                    }]
                }),
            headers={
                "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
                "Content-Type": "application/json"
            }
        )