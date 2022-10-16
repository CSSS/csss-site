import pandas
import pytz


def get_timezone_difference(date, tz1, tz2):
    """
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    """
    tz1_timezone = pytz.timezone(tz1)
    tz2_timezone = pytz.timezone(tz2)
    date = pandas.to_datetime(date)
    return (tz1_timezone.localize(date) - tz2_timezone.localize(date).astimezone(tz1_timezone)).seconds / 3600
