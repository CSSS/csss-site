from django.conf import settings

from about.views.Constants import CURRENT_EMAIL_MAPPINGS_URL
from csss.Gmail import Gmail


def alert_doa_to_update_email_list(sfu_officer_mailing_list_email, position_has_bitwarden_access):
    """
    Emails the DoA to let them know to update the specified email list

    Keyword Arguments
    sfu_officer_mailing_list_email -- the mailling list that has to be updated
    position_has_bitwarden_access -- indicator of it the position is supposed to have bitwarden access

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
    message = f"get latest mappings at {url}"
    if position_has_bitwarden_access:
        message += (" and let the Sys Admin know to perform a takeover "
                    "at https://vault.bitwarden.com/#/settings/emergency-access")
    success, error_message = gmail.send_email(
        f"update {sfu_officer_mailing_list_email}", message, "csss-doa-current@sfu.ca", "Director of Archives",
        from_name="SFU CSSS Website"
    )
    if not success:
        return False, error_message
    return gmail.close_connection()
