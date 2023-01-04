import datetime

import pytz
from django.conf import settings

from csss.setup_logger import Loggers


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
    successful = False
    email_datetime = None
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    try:
        email_datetime = datetime.datetime.strptime(email_date, date_format).astimezone(
            pytz.timezone(settings.WEBSITE_TIME_ZONE)
        )
        successful = True
    except ValueError:
        logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                    f"does not match format '{date_format}'")
    if not successful:
        date_format = '%a, %d %b %Y %H:%M:%S %z'
        try:
            email_datetime = datetime.datetime.strptime(email_date[:-6], date_format).astimezone(
                pytz.timezone(settings.WEBSITE_TIME_ZONE)
            )
            successful = True
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date[:-6]}' "
                        f"does not match format '{date_format}'")
    if not successful:
        date_format = '%a, %d %b %Y %H:%M:%S %Z'
        try:
            email_datetime = datetime.datetime.strptime(email_date, date_format).astimezone(
                pytz.timezone(settings.WEBSITE_TIME_ZONE)
            )
            successful = True
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                        f"does not match format '{date_format}'")
            email_datetime = datetime.date.today()
    if not successful:
        logger.info("[process_announcements get_date_from_email()] ultimately unable to "
                    f"determine the format for date {email_date}. Reverting to current date")
    else:
        logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                    f"from email transformed to datetime object {email_datetime}")
    email.sortable_date = email_datetime
    return email
