from about.views.input_new_officers.enter_new_officer_info.notifications.create_intro_message import \
    create_intro_message
from csss.views.send_discord_dm import send_discord_dm
from csss.views.send_email import send_email


def send_notifications_with_documentation_links(officer_obj,
                                                officer_is_executive_officer, officer_is_election_officer,
                                                officer_is_council_representative, officer_is_frosh_week_chair,
                                                officer_is_discord_manager):
    """
    Creates and send the intro to CSSS notification via the relevant channel

    Keyword Arguments
    officer_obj -- the officer that the message has to be sent to
    officer_is_executive_officer -- indicates if the officer is an executive officer
    officer_is_election_officer -- indicate if the officer is an election officer
    officer_is_council_representative -- indicates if the officer is the SFSS Council Representative
    officer_is_frosh_week_chair -- indicates if the officer is the frosh wee chair
    officer_is_discord_manager -- indicates if the officer is the discord manager

    Return
    bool -- True or false depending on if there was an issue with talking to the gmail or discord API
    error_message -- the message received alongside the error
    """
    discord_body, email_body = create_intro_message(
        officer_obj, officer_is_executive_officer, officer_is_election_officer,
        officer_is_council_representative, officer_is_frosh_week_chair, officer_is_discord_manager
    )
    subject = "Welcome to the CSSS"
    success, error_message = send_email(
        subject, email_body, f"{officer_obj.sfu_computing_id}@sfu.ca", officer_obj.full_name
    )
    if not success:
        return success, error_message
    return send_discord_dm(officer_obj.discord_id, subject, discord_body)
