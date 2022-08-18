import re

from about.views.Constants import UNPROCESSED_OFFICER_NAME__KEY, UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, \
    UNPROCESSED_OFFICER_GMAIL__KEY, \
    UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY
from resource_management.views.resource_apis.github.github_api import GitHubAPI


def validate_user_info(new_officer_info):
    """
    Ensures that the given name, announcement emails, gmail, phone number, gmail and github usernames are valid

    Keyword Arguments
    new_officer_info -- the info that the new officer has inputted about themselves

    Return
    bool -- True or False depending on if the inputted information failed validation
    error_message -- the error message if validation failed
    """
    officer_name = new_officer_info[UNPROCESSED_OFFICER_NAME__KEY]
    if ' ' not in officer_name:
        return False, f"Could not detect a full name for \"{officer_name}\" [first AND last name]"
    if len(new_officer_info[UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY].strip()) > 1:
        announcement_emails = new_officer_info[UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY].split(",")
        for announcement_email in announcement_emails:
            announcement_email = announcement_email.strip()
            if not re.match(r"^\w+@(gmail|hotmail|protonmail|sfu|outlook|icloud|me)\.(com|ca)+$", announcement_email):
                return False, f"Email \"{announcement_email}\" not recognized as a valid email"
    gmail = new_officer_info[UNPROCESSED_OFFICER_GMAIL__KEY]
    if not re.match(r"^\w+@(gmail)\.(com|ca)+$", gmail):
        return False, f"Email \"{gmail}\" not recognized as a valid gmail"
    phone_number = new_officer_info[UNPROCESSED_OFFICER_PHONE_NUMBER_KEY]
    if not ((f"{phone_number}".isdigit() and len(phone_number) == 10) or int(phone_number) == 0):
        return False, "Invalid phone number specified, please specify all 10 digits [area code and 7 digit number]"
    github_username = new_officer_info[UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY]
    github_api = GitHubAPI()
    success, error_message = github_api.validate_user(github_username)
    if not success:
        return success, error_message
    else:
        success, error_message = github_api.verify_user_in_org(github_username, invite_user=True)
        if not success:
            return success, error_message
    return True, None
