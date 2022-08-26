from csss.Gmail import Gmail


def send_email(subject, email_body, email, full_name, gmail=None, attachment=None):
    """
    Send email to the new officer with useful documentation

    Keyword Arguments
    subject -- subject to set for email
    email_body -- the intro message to send to the user, formatted for email
    email -- the email of the person to email
    full_name -- the full name of the new officer
    gmail -- an instance of the Gmail class if this function is called alot back to back so that the website does not
     have to keep authenticating against google to login
    attachment -- the logs to attach to the email if applicable

    Return
    bool -- True or False depending on if there was an issue with the google drive API
    error_message -- the error message if there was an issue
    """
    close_gmail = False
    if gmail is None:
        gmail = Gmail()
        close_gmail = True
        if not gmail.connection_successful:
            return False, gmail.error_message
    success, error_message = gmail.send_email(
        subject, email_body, email, full_name, from_name="SFU CSSS Website", attachment=attachment
    )
    if not success:
        return False, error_message
    if close_gmail:
        return gmail.close_connection()
    return True, None
