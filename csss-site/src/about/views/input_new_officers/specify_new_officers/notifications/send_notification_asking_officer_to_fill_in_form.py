from about.views.input_new_officers.specify_new_officers.notifications.\
    create_message_for_inputting_officer_info import \
    create_message_for_inputting_officer_info
from csss.views.send_discord_dm import send_discord_dm


def send_notification_asking_officer_to_fill_in_form(recipient_id, full_name, first_time_officer):
    """
    Will DM the user to alert or remind them to fill in the UnProcessed Officer form

    Keyword Arguments
    recipient_id -- the discord ID of the UnProcessed Officer
    full_name -- the full name of the UnProcessed Officer
    first_time_officer -- boolean to indicate if this is a repeat officer or someone who has never been an officer

    Return
    bool -- indicate if DM was successfully sent
    error_message -- error message to indicate why the DM was not successfully sent
    """
    return send_discord_dm(
        recipient_id,
        "Enter Information",
        create_message_for_inputting_officer_info(full_name, first_time_officer)
    )
