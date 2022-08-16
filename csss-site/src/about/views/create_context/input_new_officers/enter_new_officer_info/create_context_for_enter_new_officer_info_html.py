from about.models import Officer
from about.views.Constants import UNPROCESSED_OFFICER_NAME__KEY, UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, \
    UNPROCESSED_OFFICER_GMAIL__KEY, UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, \
    UNPROCESSED_OFFICER_COURSE_1__KEY, UNPROCESSED_OFFICER_COURSE_2__KEY, UNPROCESSED_OFFICER_LANGUAGE_1__KEY, \
    UNPROCESSED_OFFICER_LANGUAGE_2__KEY, UNPROCESSED_OFFICER_BIO__KEY, \
    OFFICER_POSITION_HAS_GOOGLE_DRIVE_ACCESS__HTML_VALUE, UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE, \
    OFFICER_POSITION_HAS_GITHUB_ACCESS__HTML_VALUE, INPUT_UNPROCESSED_OFFICER_NAME__NAME, \
    INPUT_UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__NAME, \
    INPUT_UNPROCESSED_OFFICER_GMAIL__NAME, INPUT_UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__NAME, \
    INPUT_UNPROCESSED_OFFICER_RESEND_GMAIL_VERIFICATION_CODE__NAME, \
    INPUT_UNPROCESSED_OFFICER_RESEND_VERIFICATION_CODE__VALUE, \
    INPUT_UNPROCESSED_OFFICER_PHONE_NUMBER__NAME, INPUT_UNPROCESSED_OFFICER_GITHUB_USERNAME__NAME, \
    INPUT_UNPROCESSED_OFFICER_COURSE1__NAME, \
    INPUT_UNPROCESSED_OFFICER_COURSE2__NAME, INPUT_UNPROCESSED_OFFICER_LANGUAGE1__NAME, \
    INPUT_UNPROCESSED_OFFICER_LANGUAGE2__NAME, INPUT_UNPROCESSED_OFFICER_BIO__NAME, \
    INPUT_UNPROCESSED_OFFICER_NAME__VALUE, INPUT_UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__VALUE, \
    INPUT_UNPROCESSED_OFFICER_GMAIL__VALUE, \
    INPUT_UNPROCESSED_OFFICER_PHONE_NUMBER__VALUE, INPUT_UNPROCESSED_OFFICER_GITHUB_USERNAME__VALUE, \
    INPUT_UNPROCESSED_OFFICER_COURSE1__VALUE, \
    INPUT_UNPROCESSED_OFFICER_COURSE2__VALUE, INPUT_UNPROCESSED_OFFICER_LANGUAGE1__VALUE, \
    INPUT_UNPROCESSED_OFFICER_LANGUAGE2__VALUE, \
    INPUT_UNPROCESSED_OFFICER_BIO__VALUE, RE_SEND_GMAIL_VERIFICATION_CODE, UNPROCESSED_OFFICER_START_DATE, \
    UNPROCESSED_OFFICER_TERM, UNPROCESSED_OFFICER_YEAR, UNPROCESSED_OFFICER_POSITION_NAME, \
    TAKE_IN_UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE, REDIRECT_GMAIL_VERIFICATION_CODE_BUTTON_STRING
from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html


def create_context_for_enter_new_officer_info_html(context, username, officer_emaillist_and_position_mappings,
                                                   unprocessed_officers, error_messages=None, officer_info=None,
                                                   position_info=None):
    """
    Populated the context dictionary that is used by
    about/templates/about/input_new_officers/enter_new_officer_info/enter_new_officer_info.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the enter_new_officer_info.html
    username -- the username if the user that is logged in, will be their sfu_computing_id
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    unprocessed_officers -- the queryset of currently saved unprocessed officers
    error_messages -- the list of error to display
    officer_info -- dict containing the info for the officer that they themselves inputted
    position_info -- the position mapping obj for the position the new officer is for

    """
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    context.update({
        INPUT_UNPROCESSED_OFFICER_NAME__NAME: UNPROCESSED_OFFICER_NAME__KEY,
        INPUT_UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__NAME: UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY,
        INPUT_UNPROCESSED_OFFICER_GMAIL__NAME: UNPROCESSED_OFFICER_GMAIL__KEY,
        INPUT_UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__NAME:
            UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE,
        INPUT_UNPROCESSED_OFFICER_RESEND_GMAIL_VERIFICATION_CODE__NAME: RE_SEND_GMAIL_VERIFICATION_CODE,
        INPUT_UNPROCESSED_OFFICER_RESEND_VERIFICATION_CODE__VALUE: REDIRECT_GMAIL_VERIFICATION_CODE_BUTTON_STRING,
        INPUT_UNPROCESSED_OFFICER_PHONE_NUMBER__NAME: UNPROCESSED_OFFICER_PHONE_NUMBER_KEY,
        INPUT_UNPROCESSED_OFFICER_GITHUB_USERNAME__NAME: UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY,
        INPUT_UNPROCESSED_OFFICER_COURSE1__NAME: UNPROCESSED_OFFICER_COURSE_1__KEY,
        INPUT_UNPROCESSED_OFFICER_COURSE2__NAME: UNPROCESSED_OFFICER_COURSE_2__KEY,
        INPUT_UNPROCESSED_OFFICER_LANGUAGE1__NAME: UNPROCESSED_OFFICER_LANGUAGE_1__KEY,
        INPUT_UNPROCESSED_OFFICER_LANGUAGE2__NAME: UNPROCESSED_OFFICER_LANGUAGE_2__KEY,
        INPUT_UNPROCESSED_OFFICER_BIO__NAME: UNPROCESSED_OFFICER_BIO__KEY

    })
    new_officer = unprocessed_officers.filter(sfu_computing_id=username).first()
    if position_info is None:
        position_info = officer_emaillist_and_position_mappings.filter(
            position_name=new_officer.position_name
        ).first()
    officer_name = ""
    officer_announcement_emails = ""
    officer_gmail = ""
    officer_phone_number = ""
    officer_github = ""
    officer_course1 = ""
    officer_course2 = ""
    officer_language1 = ""
    officer_language2 = ""
    officer_bio = ""
    if officer_info is not None:
        officer_name = officer_info.get(UNPROCESSED_OFFICER_NAME__KEY, officer_name)
        officer_announcement_emails = officer_info.get(
            UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, officer_announcement_emails
        )
        officer_gmail = officer_info.get(UNPROCESSED_OFFICER_GMAIL__KEY, officer_gmail)
        officer_phone_number = officer_info.get(UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, officer_phone_number)
        officer_github = officer_info.get(UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, officer_github)
        officer_course1 = officer_info.get(UNPROCESSED_OFFICER_COURSE_1__KEY, officer_course1)
        officer_course2 = officer_info.get(UNPROCESSED_OFFICER_COURSE_2__KEY, officer_course2)
        officer_language1 = officer_info.get(UNPROCESSED_OFFICER_LANGUAGE_1__KEY, officer_language1)
        officer_language2 = officer_info.get(UNPROCESSED_OFFICER_LANGUAGE_2__KEY, officer_language2)
        officer_bio = officer_info.get(UNPROCESSED_OFFICER_BIO__KEY, officer_bio)
    else:
        officer = Officer.objects.all().filter(sfu_computing_id=username).order_by('-start_date').first()
        if officer is not None:
            officer_name = officer.full_name
            officer_announcement_emails = ", ".join(
                [email.email for email in officer.announcementemailaddress_set.all()])
            officer_gmail = officer.gmail
            officer_phone_number = officer.phone_number
            officer_github = officer.github_username
            officer_course1 = officer.course1
            officer_course2 = officer.course2
            officer_language1 = officer.language1
            officer_language2 = officer.language2
            officer_bio = officer.bio

    context[UNPROCESSED_OFFICER_TERM] = new_officer.term.term
    context[UNPROCESSED_OFFICER_YEAR] = new_officer.term.year
    context[UNPROCESSED_OFFICER_POSITION_NAME] = new_officer.position_name
    context[UNPROCESSED_OFFICER_START_DATE] = new_officer.start_date
    context[INPUT_UNPROCESSED_OFFICER_NAME__VALUE] = officer_name
    context[INPUT_UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__VALUE] = officer_announcement_emails
    context[OFFICER_POSITION_HAS_GOOGLE_DRIVE_ACCESS__HTML_VALUE] = position_info.google_drive
    context[INPUT_UNPROCESSED_OFFICER_GMAIL__VALUE] = officer_gmail
    context[TAKE_IN_UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE] = (
        new_officer.gmail_verification_code is not None
    )
    context[UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE] = new_officer.gmail_verification_code is not None
    context[INPUT_UNPROCESSED_OFFICER_PHONE_NUMBER__VALUE] = officer_phone_number
    context[OFFICER_POSITION_HAS_GITHUB_ACCESS__HTML_VALUE] = (
        len(position_info.officerpositiongithubteammapping_set.all()) > 0
    ) or position_info.position_name == "Systems Administrator"
    context[INPUT_UNPROCESSED_OFFICER_GITHUB_USERNAME__VALUE] = officer_github
    context[INPUT_UNPROCESSED_OFFICER_COURSE1__VALUE] = officer_course1
    context[INPUT_UNPROCESSED_OFFICER_COURSE2__VALUE] = officer_course2
    context[INPUT_UNPROCESSED_OFFICER_LANGUAGE1__VALUE] = officer_language1
    context[INPUT_UNPROCESSED_OFFICER_LANGUAGE2__VALUE] = officer_language2
    context[INPUT_UNPROCESSED_OFFICER_BIO__VALUE] = officer_bio
