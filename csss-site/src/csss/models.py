from django.conf import settings
from django.db import models
from django.utils import timezone

from csss.PSTDateTimeField import PSTDateTimeField


class CronJob(models.Model):
    job_name = models.CharField(
        max_length=5000,
        unique=True
    )
    job_id = models.CharField(
        max_length=100,
        unique=True,
        null=True
    )
    schedule = models.CharField(
        max_length=500
    )

    @property
    def is_active(self):
        return self.schedule.strip() != ""

    last_update = PSTDateTimeField(
        default=timezone.now
    )

    @property
    def get_average_run_time(self):
        seconds_so_far = 0
        number_of_run_times = len(self.cronjobrunstat_set.all())
        if number_of_run_times == 0:
            return "&nbsp;NA"
        for seconds in self.cronjobrunstat_set.all():
            seconds_so_far += seconds.run_time_in_seconds
        seconds_so_far = seconds_so_far / number_of_run_times
        return convert_seconds_to_run_time_str(seconds_so_far)

    def __str__(self):
        return f"Job {self.job_name} with schedule {self.schedule}"


class CronJobRunStat(models.Model):
    job = models.ForeignKey(
        CronJob,
        on_delete=models.CASCADE,
    )
    run_date = PSTDateTimeField(
        default=timezone.now
    )

    run_time_in_seconds = models.IntegerField()

    @property
    def get_run_time(self):
        return convert_seconds_to_run_time_str(self.run_time_in_seconds)

    def __str__(self):
        return f"job {self.job} ran for {self.get_run_time} on {self.run_date}"


PROD_SERVER_BASE_DIR = "/home/csss"


class CSSSError(models.Model):
    type = models.CharField(
        max_length=100,
        default=None,
        null=True
    )
    base_directory = settings.BASE_DIR

    file_path = models.CharField(
        max_length=500,
        default=None,
        null=True
    )
    filename = models.CharField(
        max_length=500
    )
    message = models.CharField(
        max_length=5000
    )
    request = models.CharField(
        max_length=100000,
        default=None,
        null=True
    )
    fixed = models.BooleanField(
        default=False
    )

    @property
    def get_prod_error_absolute_path(self):
        return f"{PROD_SERVER_BASE_DIR}/{self.file_path}/{self.get_error_file_name}"

    @property
    def get_prod_debug_absolute_path(self):
        return f"{PROD_SERVER_BASE_DIR}/{self.file_path}/{self.get_debug_file_name}"

    @property
    def get_error_absolute_path(self):
        return f"{self.base_directory}/{self.file_path}/{self.get_error_file_name}"

    @property
    def get_debug_absolute_path(self):
        return f"{self.base_directory}/{self.file_path}/{self.get_debug_file_name}"

    @property
    def get_error_project_path(self):
        return f"{self.file_path}/{self.get_error_file_name}"

    @property
    def get_debug_project_path(self):
        return f"{self.file_path}/{self.get_debug_file_name}"

    @property
    def get_error_file_name(self):
        return self.filename

    @property
    def get_debug_file_name(self):
        return f"{self.filename[:-10]}_debug.log"

    endpoint = models.CharField(
        max_length=500,
        default=None,
        null=True
    )
    processed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Error in file {self.filename}"


def convert_seconds_to_run_time_str(seconds):
    hours, minutes = 0, 0
    if seconds > 60:
        minutes = int(int(seconds) / 60)
        if minutes > 60:
            hours = int(int(minutes) / 60)
            minutes = minutes % 60
    seconds = int(seconds % 60)
    run_time_str = ""
    if hours > 0:
        if hours >= 10:
            run_time_str += f"{hours:{3}} "
        else:
            run_time_str += f"{hours:{2}} "
        run_time_str += "hours"
    if minutes > 0:
        if len(run_time_str) > 0:
            run_time_str += ","
        if seconds == 0:
            run_time_str += " and "
        if minutes >= 10:
            run_time_str += f"{minutes:{3}} "
        else:
            run_time_str += f"{minutes:{2}} "
        run_time_str += "minutes"
    if seconds > 0:
        if len(run_time_str) > 0:
            run_time_str += ", and"
        if seconds >= 10:
            run_time_str += f"{seconds:{3}} "
        else:
            run_time_str += f"{seconds:{2}} "
        run_time_str += "seconds"
    if run_time_str == "":
        run_time_str = " 0 seconds"
    run_time_str = run_time_str.replace(" ", "&nbsp;")
    return run_time_str
