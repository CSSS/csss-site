import re


def validate_announcement_emails(announcement_emails):
    announcement_emails = announcement_emails.split(",")
    for announcement_email in announcement_emails:
        announcement_email = announcement_email.strip()
        if not re.match(r"^\w+@(gmail|hotmail|protonmail|sfu|outlook|icloud|me)\.(com|ca)+$", announcement_email):
            return False, f"Email {announcement_email} not recognized as a valid email"
    return True, None