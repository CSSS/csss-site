from about.models import Officer
from csss.setup_logger import get_logger

logger = get_logger()


def create_intro_message(officer_obj, officer_is_executive_officer,
                         officer_is_election_officer, officer_is_council_representative,
                         officer_is_frosh_week_chair, officer_is_discord_manager):
    """
    Creates the intro message for various officer positions

    Keyword Argument
    officer_obj -- the officer that the message has to be sent to
    officer_is_executive_officer -- indicates if the officer is an executive officer
    officer_is_election_officer -- indicate if the officer is an election officer
    officer_is_council_representative -- indicates if the officer is the SFSS Council Representative
    officer_is_frosh_week_chair -- indicates if the officer is the frosh wee chair
    officer_is_discord_manager -- indicates if the officer is the discord manager


    Return
    discord_body -- the intro message to send to the user, formatted for discord markdown
    email_body -- the intro message to send to the user, formatted for email
    """
    full_name = officer_obj.full_name
    sfu_computing_id = officer_obj.sfu_computing_id
    position_name = officer_obj.position_name
    logger.info(
        "[about/create_intro_message.py create_intro_message()] "
        f"sending email and discord notification to user {officer_obj} who is in the officer position "
        f"{position_name}"
    )
    first_time_officer = (
        Officer.objects.all().filter(sfu_computing_id=sfu_computing_id, position_name=position_name).first() is None
    )
    discord_body = email_body = f"Hello {full_name},\n\n"
    if officer_is_executive_officer:
        if first_time_officer:
            email_body += (
                "Congrats on becoming a CSSS Executive Officer.\n\n"
                "Please take some time to read our documentation: https://github.com/CSSS/documents/wiki \n\n"
            )
            discord_body += (
                "Congrats on becoming a CSSS Executive Officer.\n\n"
                "Please take some time to read [our documentation](https://github.com/CSSS/documents/wiki)"
                " :smiley:\n\n"
            )
        else:
            email_body += f"Seems like you are a repeat {position_name}.\n\n"
            discord_body += f"Seems like you are a repeat {position_name}.\n\n"
            email_body += (
                "Forgive this reminder about our digital resources: https://github.com/CSSS/documents/wiki\n\n"
            )
            discord_body += (
                "Forgive this reminder about our [digital resources](https://github.com/CSSS/documents/wiki)"
                " :smiley: \n\n"
            )
        email_body += "It includes information on \n\n"
        discord_body += "It includes information on \n\n"
        email_body += (
            " - List of our digital resources and what "
            "their intended use is: https://github.com/CSSS/documents/wiki\n\n"
            " - Transfer Guides: https://github.com/CSSS/documents/wiki/Transfer-Guides\n\n"
            " - Guidelines on how to hold Info Session Events: "
            "https://github.com/CSSS/documents/wiki/Info-Sessional-Events\n\n"
            " - Useful Contacts: https://github.com/CSSS/documents/wiki/Contacts-and-Room-Bookings\n\n\n"
            "Website Resources:"
            "In addition, we have the following resources on our website that may be of used to you:\n\n"
            " - Contact Information for current and past Officers:\n"
            "   - http://sfucsss.org/login?next=/about/list_of_current_officers\n"
            "   - http://sfucsss.org/login?next=/about/list_of_past_officers\n\n"
            " - Photo Gallery Links for uploading media from CSSS events\n"
            "   - Gallery Link: https://vault.sfu.ca/index.php/s/Z4JEfabBnAnbOcA\n"
            "   - Gallery Upload Link: https://vault.sfu.ca/index.php/s/zCHRkcCR8QHAZpg\n\n"
            " - Misc CSSS Links:\n"
            "   - CSSS Recommended Software: https://sfucsss.org/statics/guide\n"
            "   - Bursaries for CS Students: https://sfucsss.org/statics/bursaries"
        )
        discord_body += (
            " - [List of our digital resources and what their intended use is]"
            "(https://github.com/CSSS/documents/wiki) \n\n"
            " - [Transfer Guides](https://github.com/CSSS/documents/wiki/Transfer-Guides) \n\n"
            " - [Guidelines on how to hold Info Session Events](https://github.com/CSSS/"
            "documents/wiki/Info-Sessional-Events) \n\n"
            " - [Useful Contacts](https://github.com/CSSS/documents/wiki/Contacts-and-Room-Bookings) \n\n"
            "Website Resources:"
            "In addition, we have the following resources on our website that may be of used to you:\n\n"
            " - Contact Information for [current](http://sfucsss.org/login?next=/about/list_of_current_officers)"
            " and [past](http://sfucsss.org/login?next=/about/list_of_past_officers) Officers\n"
            " - [Uploading media from CSSS Events](https://vault.sfu.ca/index.php/s/zCHRkcCR8QHAZpg)\n\n"
            " - [Photos from Past CSSS Events](https://vault.sfu.ca/index.php/s/Z4JEfabBnAnbOcA)\n\n"
            " - Misc CSSS Links:\n"
            "   - [CSSS Recommended Software](https://sfucsss.org/statics/guide)\n"
            "   - [Bursaries for CS Students](https://sfucsss.org/statics/bursaries)\n"
        )

    elif officer_is_election_officer:
        if first_time_officer:
            email_body += (
                f"Congrats on becoming a CSSS {position_name}.\n\n"
                "Please read the following documentation: https://github.com/CSSS/elections-documentation"
            )
            discord_body += (
                f"Congrats on becoming a CSSS {position_name}.\n\n"
                "Please read the [following documentation]"
                "(https://github.com/CSSS/elections-documentation) :smiley: \n\n"
            )
        else:
            email_body += (
                f"Seems like you are a repeat {position_name}.\n\n"
                "Forgive this reminder about the election documentation: https://"
                "github.com/CSSS/elections-documentation"
            )
            discord_body += (
                f"Seems like you are a repeat {position_name}.\n\n"
                "Forgive this reminder about the [election documentation]"
                "(https://github.com/CSSS/elections-documentation) :smiley: \n\n"
            )
    elif officer_is_council_representative:
        if first_time_officer:
            message = f"Congrats on becoming a CSSS's {position_name}.\n\n"
        else:
            message = f"Seems like you are a repeat {position_name}.\n\n"
        message += (
            "Should you need it, you have been given access to the CSSS Google Drive, "
            "you can access it via the \"Shared\" section on your google drive"
        )
        email_body += message
        discord_body += message
    elif officer_is_frosh_week_chair:
        if first_time_officer:
            email_body += (
                f"Congrats on becoming a CSSS {position_name}.\n\n"
                "You may find the following documentation useful:\n\n"
                " - Frosh Week archive in the documents repo:  https://github.com/CSSS/documents/"
                "tree/master/froshweek\n\n"
                " - Frosh Week archive on the Google Drive: https://drive.google.com/drive/u/0/"
                "folders/0B3DzwBe8wwp2fmI0bE83cDhkSUVBQXlGNElLNnpjbzNlc3RuNm94eG9keDN6THkxeEJxV1U\n\n"
            )
            discord_body += (
                f"Congrats on becoming a CSSS {position_name}.\n\n"
                "You may find the following documentation useful:\n\n"
                " - [Frosh Week archive in the documents repo](https://github.com/CSSS/documents/"
                "tree/master/froshweek)\n\n"
                " - [Frosh Week archive on the Google Drive](https://drive.google.com/drive/u/0/"
                "folders/0B3DzwBe8wwp2fmI0bE83cDhkSUVBQXlGNElLNnpjbzNlc3RuNm94eG9keDN6THkxeEJxV1U)"
            )
        else:
            email_body += (
                f"Seems like you are a repeat {position_name}.\n\n"
                "Forgive this reminder about the Frosh Week Chair documentation:\n\n"
                " - Frosh Week archive in the documents repo:  https://github.com/CSSS/documents/"
                "tree/master/froshweek\n\n"
                " - Frosh Week archive on the Google Drive: https://drive.google.com/drive/u/0/"
                "folders/0B3DzwBe8wwp2fmI0bE83cDhkSUVBQXlGNElLNnpjbzNlc3RuNm94eG9keDN6THkxeEJxV1U\n\n"
            )
            discord_body += (
                f"Seems like you are a repeat {position_name}.\n\n"
                "Forgive this reminder about the Frosh Week Chair documentation:\n\n"
                " - [Frosh Week archive in the documents repo](https://github.com/CSSS/documents/"
                "tree/master/froshweek)\n\n"
                " - [Frosh Week archive on the Google Drive](https://drive.google.com/drive/u/0/"
                "folders/0B3DzwBe8wwp2fmI0bE83cDhkSUVBQXlGNElLNnpjbzNlc3RuNm94eG9keDN6THkxeEJxV1U)"
            )
    elif officer_is_discord_manager:
        body = (
            f"Congrats on becoming the CSSS {position_name}.\n\n"
            "Please let the Sys Admin know if you need access to any of the CSSS Digital Resouces"
        )
        email_body += body
        discord_body += body
    return discord_body, email_body
