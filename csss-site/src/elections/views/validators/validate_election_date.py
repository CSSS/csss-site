import datetime
import logging

logger = logging.getLogger('csss_site')


def validate_election_date(date):
    """
    Validates the election's date

    Keyword Argument
    date -- the inputted election date

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    try:
        datetime.datetime.strptime(f"{date}", '%Y-%m-%d %H:%M')
    except ValueError:
        error_message = f" given date of {date} is not in the valid format"
        logger.error(
            "[elections/validate_election_type.py validate_inputted_election_json()]"
            f"{error_message}"
        )
        return False, error_message
    except TypeError as e:
        error_message = "given date seems to be unreadable"
        logger.error(
            f"[elections/validate_election_type.py validate_inputted_election_json()]"
            f" {error_message} due to following error \n{e}"
        )
        return False, error_message
    return True, None
