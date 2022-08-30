from django.conf import settings

from about.views.Constants import CURRENT_EMAIL_MAPPINGS_URL
from csss.Gmail import Gmail


def alert_sys_admin_to_update_email_list(sfu_officer_mailing_list_email):
    """
    Emails the sys admin to let them know to update the specified email list

    Keyword Arguments
    sfu_officer_mailing_list_email -- the mailling list that has to be updated

    Return
    bool -- True or False depending on if there was an issue with sending an email via gmail
    error_message -- the error message if there was an issue
    """
    gmail = Gmail()
    if not gmail.connection_successful:
        return False, gmail.error_message

    url = f'http://{settings.HOST_ADDRESS}'
    if settings.DEBUG:
        url += f":{settings.PORT}"
    url += f'/about/{CURRENT_EMAIL_MAPPINGS_URL}'
    success, error_message = gmail.send_email(
        f"update {sfu_officer_mailing_list_email}", url, "csss-sysadmin@sfu.ca", "jace",
        from_name="SFU CSSS Website"
    )
    if not success:
        return False, error_message
    return gmail.close_connection()
