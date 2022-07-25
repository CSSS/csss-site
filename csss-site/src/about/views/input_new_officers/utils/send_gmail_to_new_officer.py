from csss.Gmail import Gmail


def send_gmail_to_new_officer(subject, email_body, sfu_computing_id, full_name):
    """
    Send email to the new officer with useful documentation

    Keyword Arguments
    subject -- subject to set for email
    email_body -- the intro message to send to the user, formatted for email
    sfu_computing_id -- the sfu_computing_id of the new officer that will be emailed
    full_name -- the full name of the new officer

    Return
    bool -- True or False depending on if there was an issue with the google drive API
    error_message -- the error message if there was an issue
    """
    gmail = Gmail()
    if not gmail.connection_successful:
        return False, gmail.error_message
    success, error_message = gmail.send_email(
        subject, email_body, f"{sfu_computing_id}@sfu.ca", full_name, from_name="SFU CSSS Website"
    )
    if not success:
        return False, error_message
    return gmail.close_connection()
