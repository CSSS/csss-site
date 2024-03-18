import json
from time import sleep

import requests
from django.conf import settings

from csss.settings import discord_header


def send_discord_group_message(recipient_id, title, message, text_content=None):
    """
    Will send an embed in the group chat with the specified ID

    Keyword Arguments
    recipient_id -- the channel ID of the group chat
    title -- the title for the embed
    text_content -- the text content of the message so folks can be tagged
    message -- the message for the embed

    Return
    bool -- indicate if group chat message was successfully sent
    error_message -- error message to indicate why the group chat message was not successfully sent
    """
    if settings.ENVIRONMENT == "LOCALHOST":
        recipient_id = settings.DEV_DISCORD_ID
        sleep(1)
    response = requests.post(
        f"https://discord.com/api/channels/{recipient_id}/messages",
        data=json.dumps(
            {
                "tts": False,
                "content": text_content,
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
            f"Unable to send message to channel with ID {recipient_id} due to reason '{response.reason}' with "
            f"an error message of '{json.loads(response.text)['message']}'"
        )
        return False, error_message
