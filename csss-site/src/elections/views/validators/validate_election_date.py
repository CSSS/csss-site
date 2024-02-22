import datetime

from csss.setup_logger import Loggers
from csss.views.time_converter import create_pst_time
from csss.views_helper import DATE_FORMAT
from elections.views.Constants import DATE_AND_TIME_FORMAT


def validate_json_election_date_and_time(date_and_time):
    """
    Validates the election's date from JSON

    Keyword Argument
    date -- the inputted election date and time

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    return _validate_date(date_and_time, date_type="Election Start Date")


def validate_webform_election_date_and_time(date, time, new_election=False):
    """
    Validates the election's date from WebForm

    Keyword Argument
    date -- the inputted election date
    date -- the inputted election time

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    success, error_message = _validate_date(f"{date} {time}", date_type="Election Start Date")
    if success:
        start_date = date.split(r"-")
        start_date = create_pst_time(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]))
        today_date = datetime.datetime.now()
        today_date = create_pst_time(today_date.year, today_date.month, today_date.day)
        election_start_date_in_future = today_date < start_date
        if not election_start_date_in_future and new_election:
            return False, "seems like somehow this election is starting in the past."
        # decided to allow election officers to spend 3 weeks maximum reaching out to nominees
        if (start_date - today_date).days > (7 * 3):
            return False, (
                "You are trying to create an election 3 weeks before it is public. Please select a date closer"
                " to current date"
            )
        return True, None
    return success, error_message


def validate_webform_election_end_date(end_date_str, start_date_str):
    """
    Validates the election's date from WebForm

    Keyword Argument
    end_date_str -- the inputted election end date in str format
    start_date_str -- the inputted election start date in str format

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    start_date = start_date_str.split(r"-")
    start_date = create_pst_time(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]))
    success, error_message = _validate_date(f"{end_date_str}", include_time=False, date_type="Election End Date")
    if success:
        end_date = end_date_str.split(r"-")
        end_date_year = int(end_date[0])
        end_date_month = int(end_date[1])
        end_date_day = int(end_date[2])
        end_date = create_pst_time(year=end_date_year, month=end_date_month, day=end_date_day)
        if end_date <= start_date:
            return False, "Seems that the end date is on the same day as the start date or before it"
        if (end_date - start_date).days > (7 * 3):
            return False, (
                "An election cannot run for more than 3 weeks. the average is typically a week and half"
            )
        return True, None
    else:
        # comes here if the end date is not valid, This can either mean the user entered an incorrect date format
        # somehow or there just wasn't an end date specified
        # if there wasn't an end date specified but its for a past election, then it's possible that election results
        # was processed already and someone is updating a past election for some reason. In which an empty end date
        # [which means null] is valid

        current_date = datetime.datetime.now()
        # assuming it's a current election if the start_date is less than 7 days ago
        current_election = (create_pst_time(current_date.year, current_date.month,
                                            current_date.day) - start_date).days < 7
        if end_date_str == "" and not current_election:
            # if the end date is empty [which means None] but It's for a past election,
            # then an empty end date is expected as It's what happens when its election results
            # have already been processed.
            return True, None

        if end_date_str == "":
            return False, "Did not give an end date for the election"

        return success, error_message


def _validate_date(date, include_time=True, date_type=None):
    """
    Validates the election's date

    Keyword Argument
    date -- the inputted election date
    include_time -- flag to indicate whether the date also includes the time in it
    date_type -- string to indicate if the date is for Voting Start Date or End Date

    Return
    sucess -- Bool
    error_message -- an error message if the date was badly formatted, otherwise it is None
    """
    logger = Loggers.get_logger()
    try:
        if include_time:
            datetime.datetime.strptime(f"{date}", DATE_AND_TIME_FORMAT)
        else:
            datetime.datetime.strptime(f"{date}", DATE_FORMAT)
    except ValueError:
        error_message = f" given date of '{date}' is not in the valid format"
        if date_type:
            error_message += f" for {date_type}"
        logger.warning(
            "[elections/validate_election_date.py _validate_date()]"
            f"{error_message}"
        )
        return False, error_message
    except TypeError as e:
        error_message = "given date seems to be unreadable"
        if date_type:
            error_message += f" for {date_type}"
        logger.warning(
            f"[elections/validate_election_date.py _validate_date()]"
            f" {error_message} due to following error \n{e}"
        )
        return False, error_message
    return True, None
