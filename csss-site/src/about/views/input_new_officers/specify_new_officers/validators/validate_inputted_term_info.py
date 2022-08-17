import datetime

from about.models import Term


def validate_inputted_term_info(inputted_term, inputted_year):
    """
    validate the inputted term and year to ensure the new officers are being assigned to a valid term

    Keyword Argument
    inputted_term -- the term that the new officers were voted in
    inputted_year -- the year that the new officers were voted in

    Return
    bool -- indicator of whether the validation was successful
    error_message -- whatever error message there was as a result of the validation, or None
    """
    if inputted_term not in [term_choice[0] for term_choice in Term.term_choices]:
        return False, f"Invalid term [{inputted_term}] was specified"

    if not f"{inputted_year}".isdigit():
        return False, f"inputted year of {inputted_year} is not a number"

    valid_years = [
        year for year in reversed(
            list(
                range(
                    1970,
                    datetime.datetime.now().year + (1 if int(datetime.datetime.now().month) <= 8 else 2)
                )
            )
        )
    ]

    if int(inputted_year) not in valid_years:
        return False, f"Invalid year of {inputted_year} was specified"
    return True, None
