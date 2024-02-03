import datetime
import re

import pytz
from dateutil.tz import tz, tzfile
from django.db import models


class pstdatetime(datetime.datetime):  # noqa: N801
    """
    Create a pstdatetime object representing current object
    pstdatetime.now()

    Converting datetime.datetime to pstdatetime
    if the numbers in the datetime.datetime object are already in pacific time
    pstdatetime.from_datetime_with_pst_time(datetime_object)

    if the numbers in the datetime.datetime object are in UTC time
    pstdatetime.from_utc_datetime(datetime_object)

    creating object from epoch time
    pstdatetime.from_epoch(datetime_object)
    """

    PACIFIC_TZ = tz.gettz('Canada/Pacific')
    UTC_TZ = pytz.UTC

    @property
    def pst(self):
        return self.astimezone(self.PACIFIC_TZ) if self.tzinfo == self.UTC_TZ else self

    @property
    def utc(self):
        return self if self.tzinfo == self.UTC_TZ else self.astimezone(self.UTC_TZ)

    @classmethod
    def now(cls, tz=None):
        return super(pstdatetime, cls).now(tz=cls.PACIFIC_TZ)

    @classmethod
    def from_utc_datetime(cls, date: datetime.datetime):
        return pstdatetime(
            date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute, second=date.second,
            microsecond=date.microsecond, tzinfo=cls.UTC_TZ
        )

    @classmethod
    def from_datetime_with_pst_time(cls, datetime_obj):
        """
        Creates a PST timezone object using a datetime object

        Keyword Arguments
        datetime_obj -- the datetime with the day and time to use to create the PST timezone object

        Return
        datetime -- the PST timezone object
        """
        return pstdatetime(
            year=datetime_obj.year, month=datetime_obj.month, day=datetime_obj.day, hour=datetime_obj.hour,
            minute=datetime_obj.minute, second=datetime_obj.second, tzinfo=cls.PACIFIC_TZ
        )

    @classmethod
    def from_csv_epoch(cls, epoch_time: int):
        return None if epoch_time == "" else cls.from_epoch(int(epoch_time))

    @classmethod
    def from_epoch(cls, epoch_time: int):
        try:
            date = pstdatetime.fromtimestamp(epoch_time).astimezone(cls.UTC_TZ)
        except ValueError:
            date = pstdatetime.fromtimestamp(
                int(epoch_time)//1000
            ).replace(microsecond=int(epoch_time) % 1000 * 10).astimezone(cls.UTC_TZ)
        return date.pst

    @classmethod
    def create_pst_time(cls, year, month, day, hour_24=0, minute=0, second=0):
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
        return pstdatetime(
            year=year, month=month, day=day, hour=hour_24, minute=minute, second=second, tzinfo=cls.PACIFIC_TZ
        )

    @classmethod
    def create_utc_time(cls, year, month, day, hour_24=0, minute=0, second=0):
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
        return cls.create_pst_time(
                year=year, month=month, day=day, hour_24=hour_24, minute=minute, second=second
            ).utc


class NewPSTDateTimeField(models.DateTimeField):

    def pre_save(self, model_instance, add):
        """
        Makes sure to convert the date to UTC time before saving if its in Canada/Pacific timezone
        """
        from announcements.management.commands.process_announcements import SERVICE_NAME
        from csss.setup_logger import Loggers
        date = getattr(model_instance, self.attname)
        # date can be None cause of end date
        if type(date) == str and date.strip() == "":
            setattr(model_instance, self.attname, None)
        elif date is not None:
            logger = Loggers.get_logger(logger_name=SERVICE_NAME)
            logger.info(f"parsing date {date} before saving to DB")
            if type(date) is str and re.match(r"\d{4}-\d{2}-\d{2}", date):
                year = int(date[:4])
                month = int(date[5:7])
                day = int(date[8:10])
                logger.info(f"first if-parsed date to year {year} month {month} day {day}")
                final_date = pstdatetime.create_utc_time(year, month, day)
                logger.info(f"first if-{year}-{month}-{day} parsed to final_date {final_date}")
                setattr(model_instance, self.attname, final_date)
            elif date.tzinfo == tzfile('/usr/share/zoneinfo/Canada/Pacific'):
                logger.info(f"second if-{date} parsed to utc date {date.utc}")
                setattr(model_instance, self.attname, date.utc)
            elif date.tzinfo is None:
                raise Exception("no timezone detected")
        return super(NewPSTDateTimeField, self).pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        """
        Converts the value from the DB from UTC time to PST time before returning to calling code
        """
        # date can be None cause of end date
        if value is None:
            return None
        return pstdatetime.from_utc_datetime(value).pst
