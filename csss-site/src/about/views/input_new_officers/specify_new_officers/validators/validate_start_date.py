import datetime
import logging

from csss.views_helper import DATE_FORMAT

logger = logging.getLogger('csss_site')


def validate_start_date(start_date):
    """
    Ensures that the given start date for a New_Officer is a valid date

    Keyword Argument
    start_date -- the start date the New_Officer to validate

    Return
    bool -- indicator of whether the validation was successful
    error_message -- whatever error message there was as a result of the validation, or None
    """
    try:
        datetime.datetime.strptime(f"{start_date}", DATE_FORMAT)
    except ValueError:
        error_message = f" given date of {start_date} is not in the valid format"
        logger.error(
            "[about/validate_inputted_new_officers.py validate_start_date()]"
            f"{error_message}"
        )
        return False, error_message
    except TypeError as e:
        error_message = "given date seems to be unreadable"
        logger.error(
            f"[elections/validate_inputted_new_officers.py validate_start_date()]"
            f" {error_message} due to following error \n{e}"
        )
        return False, error_message
    return True, None
