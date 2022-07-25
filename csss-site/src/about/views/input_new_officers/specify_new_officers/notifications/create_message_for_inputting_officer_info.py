from django.conf import settings

from about.views.Constants import ENTER_NEW_OFFICER_INFO_URL


def create_message_for_inputting_officer_info(full_name, first_time_officer):
    """
    Creates the message to send to unprocessed officer to ask them to fill in the link to obtain their info

    Keyword Arguments
    full_name -- the full name of the unprocessed officer
    first_time_officer -- boolean that indicates if the unprocessed officer is a returning officer or a new officer

    Return
    message -- the message to send to the unprocessed officer
    """
    url = f'http://{settings.HOST_ADDRESS}'
    if settings.DEBUG:
        url += f":{settings.PORT}"
    url += f'/login?next=/about/{ENTER_NEW_OFFICER_INFO_URL}'

    if first_time_officer:
        message = (
            f"Hello {full_name},\n\nCongrats on becoming a CSSS officer. :smiley:\n\n[Click on this link to"
            f" complete the process of becoming a new officer for the CSSS]({url})"
        )
    else:
        message = (
            f"Hello {full_name},\n\nLooks like you're a repeat officer :smiley:\n\n[Please fill out this"
            f" form to get access to all the things a CSSS Officer would need]({url})"
        )
    return message
