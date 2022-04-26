import re


def validate_gmail(gmail):
    gmail = gmail.strip()
    if not re.match(r"^\w+@gmail\.com$", gmail):
        return False, f"Email {gmail} not recognized as a valid gmail"
    return True, None
