from about.views.Constants import TERM_KEY, YEAR_KEY


def ensure_term_info_are_present(inputted_term, inputted_year):
    """
    Make sure that a term and year were received from the user's request

    Keyword Argument
    inputted_term -- the term to ensure was received
    inputted_year - -the year to ensure was received

    Return
    bool -- true or false depending on if the term and year are not None
    error_message -- message if term year are None
    """
    error_message = ""
    all_required_fields_are_present = True
    if inputted_term is None or inputted_year is None:
        all_required_fields_are_present = False
        error_message = "It seems that the following field[s] are missing: "
        if inputted_term is not None:
            error_message += f"{TERM_KEY}"
        if inputted_year is not None:
            if inputted_term is not None:
                error_message += ", "
            error_message += f"{YEAR_KEY}"
    return all_required_fields_are_present, error_message
