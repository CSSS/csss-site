import datetime

from about.models import Term, NewOfficer





def validate_inputted_term_info(inputted_term, inputted_year):
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
