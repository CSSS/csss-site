import datetime
import re

import pytz
from dateutil.tz import tzfile
from django.db import models

from csss.views.time_converter import convert_utc_time_to_pacific, create_pst_time_from_datetime, \
    convert_pacific_time_to_utc, create_utc_time


class PSTDateTimeField(models.DateTimeField):

    def pre_save(self, model_instance, add):
        """
        Makes sure to convert the date to UTC time before saving if its in Canada/Pacific timezone
        """
        date = getattr(model_instance, self.attname)
        # date can be None cause of end date
        if date is not None:
            if type(date) is str and re.match(r"\d{4}-\d{2}-\d{2}", date):
                year = int(date[:4])
                month = int(date[5:7])
                day = int(date[8:])
                setattr(model_instance, self.attname, create_utc_time(year, month, day))
            elif date.tzinfo == tzfile('/usr/share/zoneinfo/Canada/Pacific'):
                setattr(model_instance, self.attname, convert_pacific_time_to_utc(date))
        return super(PSTDateTimeField, self).pre_save(model_instance, add)

    def from_db_value(self, value, expression, connection):
        """
        Converts the value from the DB from UTC time to PST time before returning to calling code
        """
        # date can be None cause of end date
        if value is not None and value.tzinfo == pytz.UTC:
            return convert_utc_time_to_pacific(value)
        if value is not None and value.tzinfo is None and type(value) is datetime:
            return create_pst_time_from_datetime(value)
        return value
