from about.views.Constants import NEW_OFFICERS__HTML_VALUE, ID_KEY, TERM_KEY, YEAR_KEY, \
    INPUT_RESEND_LINK_TO_OFFICER__HTML_VALUE, SAVE_OR_UPDATE_NEW_OFFICERS_NAME


def transform_webform_to_json(new_officers_dict):
    """
    Converts the given new officers dictionary from
     Webform into a JSON format to prepare for the
     process_specified_new_officers function

    Keyword Argument
    new_officers_dict --the dictionary that the new officers creation/update page created

    Return
    new_officers -- the list of new officers the user inputted
    inputted_term -- the term that the new officers will fall under, or None
    inputted_year -- the year that the new officers will fall under, or None
    id_of_new_officer_to_send_link_to -- if the user clicked the button to resend a DM to a saved New_Officer,
     it contains the ID of the New_Officer to send the DM to
    save_or_update_new_officers -- indicates if the user clicked the link to save/update the specified New_Officers
    """
    new_officers = []
    if NEW_OFFICERS__HTML_VALUE in new_officers_dict and type(new_officers_dict[NEW_OFFICERS__HTML_VALUE]) == dict:
        new_officers = list(new_officers_dict[NEW_OFFICERS__HTML_VALUE].values())
        for new_officer in new_officers:
            if ID_KEY in new_officer and len(new_officer[ID_KEY]) == 0:
                del new_officer[ID_KEY]
    inputted_term = None
    if TERM_KEY in new_officers_dict:
        inputted_term = new_officers_dict[TERM_KEY]
    inputted_year = None
    if YEAR_KEY in new_officers_dict:
        inputted_year = new_officers_dict[YEAR_KEY]
    id_of_new_officer_to_send_link_to = None
    for (key, value) in new_officers_dict.items():
        if value == INPUT_RESEND_LINK_TO_OFFICER__HTML_VALUE:
            id_of_new_officer_to_send_link_to = key

    save_or_update_new_officers = None
    if SAVE_OR_UPDATE_NEW_OFFICERS_NAME in new_officers_dict:
        save_or_update_new_officers = new_officers_dict[SAVE_OR_UPDATE_NEW_OFFICERS_NAME]
    return (
        new_officers, inputted_term, inputted_year, id_of_new_officer_to_send_link_to,
        save_or_update_new_officers
    )
