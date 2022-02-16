import datetime
import logging

from elections.views.Constants import DATE_AND_TIME_FORMAT

logger = logging.getLogger('csss_site')


def validate_start_date(start_date):
    try:
        datetime.datetime.strptime(f"{start_date}", DATE_AND_TIME_FORMAT)
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
