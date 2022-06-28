import json
import os

import requests

def dm_new_officers_welcome_to_the_csss(recipient_id):
    response = requests.post(
        "https://discord.com/api/users/@me/channels",
        data=json.dumps({
            "recipient_id": recipient_id
        }),
        headers={
            "Authorization": f"Bot {os.environ['TOKEN']}",
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
                        "title": f"Welcome to the CSSS",
                        "description": (
                            f"Hello Jace Manshadi, "
                            f"Congrats on becoming a CSSS Officer."
                            f"Some basic info to get you started: "
                            "## SFU CSSS's Digital Resources: "
                            "### [SFU CSSS's Github org](https://github.com/csss/)"
                            " We use github for projects like our "
                            "[website](https://github.com/CSSS/csss-site), our home-made discord bot "
                            "[wall_e](https://github.com/CSSS/wall_e) and some of the more professional oriented "
                            "repositories such as [our minutes](https://github.com/CSSS/minutes), "
                            "[public-docs](https://github.com/CSSS/public-docs) and a repo we use to store files that "
                            "are officer eyes only: [documents](https://github.com/CSSS/documents)."
                            "### SFU CSSS Google Drive"
                            "We use google drive for a bunch of things. things like tracking our most recent frosh "
                            "documentation, where we keep our transactional stuff that is related to merchandise sales "
                            "and other things. It is really used just as a data dump for officers who do not like git."
                            "The lines between our github and our google drive is rather blurry, but in general, "
                            "if something is older than 2 years, it is moved from google drive to github as we prefer "
                            "to use github for archive purposes.if you ever want to create a google doc that can be "
                            "accessible via public link, you will need to input the ID of the document into the csss "
                            "website. otherwise, after midnight, it will no longer be publicly accessible.[steps to "
                            "follow for updating ownership of files on our Google Drive.]({media.product_url})"
                            " If you don't, you will "
                            "get spammed everyday by our website."
                        )
                    }]
                }),
            headers={
                "Authorization": f"Bot {os.environ['TOKEN']}",
                "Content-Type": "application/json"
            }
        )