import datetime

from about.models import Term


def validate_inputted_term_info(inputted_term, inputted_year):
    if inputted_term not in [term_choice[0] for term_choice in Term.term_choices]:
        return False, f"Invalid term [{inputted_term}] was specified"

    if not f"{inputted_year}".isdigit():
        return False, f"inputted year of {inputted_year} is not a number"

    current_date = datetime.datetime.now()
    if int(current_date.month) <= 4:
        offset = 1
    elif int(current_date.month) <= 8:
        offset = 1
    else:
        offset = 2

    if int(inputted_year) not in [year for year in
                                  reversed(list(range(1970, datetime.datetime.now().year + offset)))]:
        return False, f"Invalid year of {inputted_year} was specified"

    return True, None
