import random
import string

from csss.Gmail import Gmail


def validate_gmail(unprocessed_officers, new_officer, gmail, gmail_verification_code, resend_verification_code=False):
    """
    Ensures that the gmail given by the new officer actually belongs to the new officer

    Keyword Argument
    unprocessed_officers -- the queryset of currently saved unprocessed officers
    new_officer -- the new officer whose given gmail has to be verified
    gmail -- the gmail that the new officer is claiming is theirs
    gmail_verification_code -- the gmail verification code that the user entered
    resend_verification_code -- indicates if the user wants the verification code sent to them again

    Return
    bool -- False if there was an issue sending the verification code or the inputted verification code was wrong
    error_message -- the error message for the above cases
    """
    if resend_verification_code or (gmail_verification_code is None):
        if new_officer.gmail_verification_code is not None:
            gmail_verification_code = new_officer.gmail_verification_code
        if gmail_verification_code is None:
            gmail_verification_code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(5))
            while len(unprocessed_officers.filter(gmail_verification_code=gmail_verification_code)) > 0:
                gmail_verification_code = ''.join(
                    random.choice(string.ascii_letters + string.digits) for i in range(5)
                )
            new_officer.gmail_verification_code = gmail_verification_code
            new_officer.save()
        gmail_api = Gmail()
        success, error_message = gmail_api.send_email(
            "SFU CSSS Verification Code", f"Passphrase is {gmail_verification_code}", gmail,
            new_officer.full_name, "SFU CSSS Website"
        )
        if not success:
            return success, error_message
        return False, None
    else:
        if new_officer.gmail_verification_code != gmail_verification_code:
            return False, "Incorrect Gmail Verification Code Entered"
        return True, None
