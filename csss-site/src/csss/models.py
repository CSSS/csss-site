import django
from django.db import models


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

    last_update = models.DateTimeField(
        default=django.utils.timezone.now
    )

    @property
    def get_average_run_time(self):
        seconds_so_far = 0
        number_of_run_times = len(self.cronjobrunstat_set.all())
        if number_of_run_times == 0:
            return "NA"
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
    run_date = models.DateTimeField(
        default=django.utils.timezone.now
    )
    run_time_in_seconds = models.IntegerField()

    @property
    def get_run_time(self):
        return convert_seconds_to_run_time_str(self.run_time_in_seconds)

    def __str__(self):
        return f"job {self.job} ran for {self.get_run_time} on {self.run_date}"


def convert_seconds_to_run_time_str(seconds):
    hours, minutes = 0, 0
    if seconds > 60:
        minutes = seconds / 60
        if minutes > 60:
            hours = minutes / 60
            minutes = minutes % 60
    seconds = seconds % 60
    run_time_str = ""
    if hours > 0:
        run_time_str += f"{hours} hours"
    if minutes > 0:
        if len(run_time_str) > 0:
            run_time_str += ","
        if seconds == 0:
            run_time_str += " and"
        run_time_str += f" {minutes} minutes"
    if seconds > 0:
        if len(run_time_str) > 0:
            run_time_str += ", and"
        run_time_str += f" {seconds} seconds"
    return run_time_str
