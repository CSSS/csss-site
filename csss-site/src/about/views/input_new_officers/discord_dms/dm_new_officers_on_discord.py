import json

import requests
from django.conf import settings

from about.views.Constants import ENTER_NEW_OFFICER_INFO_URL


def dm_new_officers_on_discord(full_name, recipient_id, first_time_officer):
    """
    Will DM the user to alert or remind them to fill in the New_Officer forms

    Keyword Arguments
    full_name -- the full name of the New_Officer
    recipient_id -- the discord ID of the New_Officer
    first_time_officer -- boolean to indicate if this is a repeat officer or someone who has never been an officer

    Return
    bool -- indicate if DM was successfully sent
    error_message -- error message to indicate why the DM was not successfully sent
    """
    recipient_id = 288148680479997963
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
        if first_time_officer:
            message = (
                "Congrats on becoming a CSSS officer. :smiley:\n\n[Click on this link to complete the process"
                " of becoming a new officer for the CSSS]"
                f"(http://127.0.0.1:8000/login?next=/about/{ENTER_NEW_OFFICER_INFO_URL})"
            )
        else:
            message = (
                "Looks like you're a repeat officer :smiley:\n\n[Please fill out this form to get access to"
                " all the things a CSSS Officer would need](http://127.0.0.1:8000/login?next=/about/"
                f"{ENTER_NEW_OFFICER_INFO_URL})"
            )
        response = requests.post(
            f"https://discord.com/api/channels/{response.json()['id']}/messages",
            data=json.dumps(
                {
                    "tts": False,
                    "embeds": [{
                        "title": "Enter Information",
                        "description": (
                            f"Hello {full_name},\n\n"
                            f"{message}"
                        )
                    }]
                }),
            headers={
                "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
                "Content-Type": "application/json"
            }
        )
    if response.status_code == 200:
        return True, None
    else:
        return False, f"Encountered error message of '{response.reason}'"

