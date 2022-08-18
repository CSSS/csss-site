from about.views.Constants import UNPROCESSED_OFFICER_NAME__KEY, UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, \
    UNPROCESSED_OFFICER_GMAIL__KEY, UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, \
    UNPROCESSED_OFFICER_COURSE_1__KEY, UNPROCESSED_OFFICER_COURSE_2__KEY, UNPROCESSED_OFFICER_LANGUAGE_1__KEY, \
    UNPROCESSED_OFFICER_LANGUAGE_2__KEY, UNPROCESSED_OFFICER_BIO__KEY, \
    UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE, RE_SEND_GMAIL_VERIFICATION_CODE


def transform_webform_to_json(new_officer_dict):
    """
    Converts the given new officers dictionary from
     Webform into a JSON format to prepare for the
     process_new_officer_info function

    Keyword Argument
    new_officers_dict --the dictionary that page that the user inputs their data into creates

    Return
    officer_info -- a dict that contains the relevant extracted data
    """
    return {
        UNPROCESSED_OFFICER_NAME__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_NAME__KEY, "").strip(),
        UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY: new_officer_dict.get(
            UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, ""
        ).strip(),
        UNPROCESSED_OFFICER_GMAIL__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_GMAIL__KEY, "").strip(),
        UNPROCESSED_OFFICER_PHONE_NUMBER_KEY: new_officer_dict.get(UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, "").strip(),
        UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY: new_officer_dict.get(
            UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, ""
        ).strip(),
        UNPROCESSED_OFFICER_COURSE_1__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_COURSE_1__KEY, "").strip(),
        UNPROCESSED_OFFICER_COURSE_2__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_COURSE_2__KEY, "").strip(),
        UNPROCESSED_OFFICER_LANGUAGE_1__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_LANGUAGE_1__KEY, "").strip(),
        UNPROCESSED_OFFICER_LANGUAGE_2__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_LANGUAGE_2__KEY, "").strip(),
        UNPROCESSED_OFFICER_BIO__KEY: new_officer_dict.get(UNPROCESSED_OFFICER_BIO__KEY, "").strip(),
        UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE: new_officer_dict[
            UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE
        ] if UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE in new_officer_dict else None,
        RE_SEND_GMAIL_VERIFICATION_CODE: RE_SEND_GMAIL_VERIFICATION_CODE in new_officer_dict
    }
