import datetime

from csss.setup_logger import Loggers
from csss.views.time_converter import create_pst_time_from_datetime


def add_sortable_date_to_email(email):
    """
    attempts to get add a sortable date to the email using a field in the email.
    Failing that, it will just return today's date.

    Keyword Argument
    email_date -- the email

    Return
    email_datetime -- the email with a new "sortable_date" field
    """
    logger = Loggers.get_logger()
    email_date = email.get_email_object().get('date')
    email_datetime = None
    date_formats = ['%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z']
    for date_format in date_formats:
        try:
            email_datetime = datetime.datetime.strptime(email_date, date_format)
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                        f"does not match format '{date_format}'")
        if email_datetime is None:
            try:
                email_datetime = datetime.datetime.strptime(email_date[:-6], date_format)
            except ValueError:
                logger.info(f"[process_announcements get_date_from_email()] date '{email_date[:-6]}' "
                            f"does not match format '{date_format}'")
        if email_datetime is not None:
            break

    if email_datetime is None:
        email_datetime = datetime.date.today()
        logger.info("[process_announcements get_date_from_email()] ultimately unable to "
                    f"determine the format for date {email_date}. Reverting to current date")

    email_datetime = create_pst_time_from_datetime(email_datetime)
    logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                f"from email transformed to datetime object {email_datetime}")
    email.sortable_date = email_datetime
    return email
