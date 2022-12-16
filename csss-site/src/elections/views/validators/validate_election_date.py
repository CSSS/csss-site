import datetime

from csss.setup_logger import get_logger
from elections.views.Constants import DATE_AND_TIME_FORMAT


def validate_json_election_date_and_time(date_and_time):
    """
    Validates the election's date from JSON

    Keyword Argument
    date -- the inputted election date

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    return _validate_date(date_and_time)


def validate_webform_election_date_and_time(date, time):
    """
    Validates the election's date from WebForm

    Keyword Argument
    date -- the inputted election date

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    return _validate_date(f"{date} {time}")


def _validate_date(date):
    """
    Validates the election's date

    Keyword Argument
    date -- the inputted election date
    date_format -- the format of the date from the JSON or WebForm

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    logger = get_logger()
    try:
        datetime.datetime.strptime(f"{date}", DATE_AND_TIME_FORMAT)
    except ValueError:
        error_message = f" given date of {date} is not in the valid format"
        logger.error(
            "[elections/validate_election_date.py _validate_date()]"
            f"{error_message}"
        )
        return False, error_message
    except TypeError as e:
        error_message = "given date seems to be unreadable"
        logger.error(
            f"[elections/validate_election_date.py _validate_date()]"
            f" {error_message} due to following error \n{e}"
        )
        return False, error_message
    return True, None
