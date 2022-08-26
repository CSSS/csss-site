import json
from time import sleep

import requests
from django.conf import settings

from csss.settings import discord_header


def send_discord_dm(recipient_id, title, message):
    """
    Will DM the user to alert or remind them to fill in the New_Officer forms

    Keyword Arguments
    recipient_id -- the discord ID of the New_Officer
    title -- the title for the embed
    message -- the message for the embed

    Return
    bool -- indicate if DM was successfully sent
    error_message -- error message to indicate why the DM was not successfully sent
    """
    if settings.ENVIRONMENT == "LOCALHOST":
        recipient_id = settings.DEV_DISCORD_ID
    response = requests.post(
        "https://discord.com/api/users/@me/channels",
        data=json.dumps({
            "recipient_id": recipient_id
        }),
        headers=discord_header
    )
    if response.status_code == 200:
        sleep(1)
        response = requests.post(
            f"https://discord.com/api/channels/{response.json()['id']}/messages",
            data=json.dumps(
                {
                    "tts": False,
                    "embeds": [{
                        "title": title,
                        "description": message
                    }]
                }),
            headers=discord_header
        )
    if response.status_code == 200:
        return True, None
    else:
        error_message = (
            f"Unable to send message to officer {recipient_id} due to reason '{response.reason}' with "
            f"an error message of '{json.loads(response.text)['message']}'"
        )
        return False, error_message
