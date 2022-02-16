import requests


def validate_discord_id(discord_id):
    resp = requests.get(
        f"https://discord.com/api/guilds/228761314644852736/members/{discord_id}",
        headers={
            "Authorization": "Bot NDgyMzk0NDYxOTkzODI4MzUz.XpQfaA.AGAf7NLBHpiwai3Cq5P6VJm5CGU"
        }
    )
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}'"
    return True, None