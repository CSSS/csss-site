import random
import string

from about.models import NewOfficer
from csss.Gmail import Gmail
from resource_management.models import GoogleMailAccountCredentials


def validate_gmail_code(gmail, gmail_code=None, new_officer=None):
    if new_officer is None:
        return False, "Could not detect the information for the new officer"
    if gmail_code is None:
        return generate_and_send_verification_code(gmail, new_officer)
    if gmail_code != new_officer.gmail_code:
        return False, "Incorrect verification code"
    return True, None


def generate_and_send_verification_code(gmail, new_officer):
    verification_code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(5))
    while len(NewOfficer.objects.all().filter(verification_code=verification_code)) > 0:
        verification_code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(5))
    new_officer.verification_code = verification_code
    new_officer.save()
    gmail_credentials = GoogleMailAccountCredentials.objects.all().filter(username="sfucsss@gmail.com")
    if len(gmail_credentials) == 0:
        return False, ("Could not find any credentials for the gmail sfucsss@gmail.com account "
                       "in order to send notification email")
    sfu_csss_credentials = gmail_credentials[0]
    gmail_api = Gmail(sfu_csss_credentials.username, sfu_csss_credentials.password)
    if not gmail_api.connection_successful:
        return False, gmail_api.error_message
    success, error_message = gmail_api.send_email(
        "SFU CSSS Verification Code", f"Passphrase is {verification_code}", gmail,
        new_officer.full_name, "SFU CSSS Website"
    )
    if not success:
        return False, error_message
    return False, "Please enter verification code that has been emailed to the specified gmail"
