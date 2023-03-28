import datetime

import pytz
from dateutil.tz import tz

TIME_ZONE = 'Canada/Pacific'


PACIFIC_TZ = tz.gettz(TIME_ZONE)
UTC_TZ = pytz.UTC


def create_pst_time(year, month, day, hour_24=0, minute=0, second=0):
    """
    Creates a PST timezone object with the given parameters

    Keyword Arguments
    year -- the year (YYYY)
    month -- the month (01-12)
    day -- the day (01-XX)
    hour_24 -- -the hour (0-23)
    minute -- the minute (0-59)
    second -- the second (0-59)

    Return
    datetime -- the PST timezone object
    """
    return datetime.datetime(
        year=year, month=month, day=day, hour=hour_24, minute=minute, second=second, tzinfo=PACIFIC_TZ
    )


def create_utc_time(year, month, day, hour_24=0, minute=0, second=0):
    """
    Creates a UTC timezone object with the given parameters

    Keyword Arguments
    year -- the year (YYYY)
    month -- the month (01-12)
    day -- the day (01-XX)
    hour_24 -- -the hour (0-23)
    minute -- the minute (0-59)
    second -- the second (0-59)

    Return
    datetime -- the UTC timezone object
    """
    return datetime.datetime.fromtimestamp(
        create_pst_time(
            year=year, month=month, day=day, hour_24=hour_24, minute=minute, second=second
        ).timestamp()
    ).astimezone(UTC_TZ)


def convert_pacific_time_to_utc(pacific_date):
    """
    Convert the given Pacific timezone object to a UTC timezone object

    Keyword Arguments
    pacific_date -- the given pacific timezone object to convert

    Return
    datetime -- the UTC timezone equivalent of the pacific_date
    """
    return datetime.datetime.fromtimestamp(pacific_date.timestamp()).astimezone(UTC_TZ)


def create_pst_time_from_datetime(datetime_obj):
    """
    Creates a PST timezone object using a datetime object

    Keyword Arguments
    datetime_obj -- the datetime with the day and time to use to create the PST timezone object

    Return
    datetime -- the PST timezone object
    """
    return datetime.datetime(
        year=datetime_obj.year, month=datetime_obj.month, day=datetime_obj.day, hour=datetime_obj.hour,
        minute=datetime_obj.minute, second=datetime_obj.second, tzinfo=PACIFIC_TZ
    )


def convert_utc_time_to_pacific(utc_datetime):
    """
    Convert the given UTC timezone object to a PST timezone object

    Keyword Arguments
    utc_datetime -- the given UTC timezone object to convert

    Return
    datetime -- the PST timezone equivalent of the utc_datetime
    """
    return utc_datetime.astimezone(PACIFIC_TZ)
