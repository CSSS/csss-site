import datetime
import time

from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import date_timezone, Loggers
from resource_management.management.commands.validate_google_drive import SERVICE_NAME
from resource_management.views.resource_views import validate_google_drive



def run_job():
    time1 = time.perf_counter()
    current_date = datetime.datetime.now(date_timezone)
    Loggers.get_logger(logger_name=SERVICE_NAME, current_date=current_date)
    validate_google_drive()
    Loggers.remove_logger(SERVICE_NAME, current_date)
    time2 = time.perf_counter()
    total_seconds = time2 - time1
    cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
    number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
    if len(number_of_stats) == 10:
        first = number_of_stats.order_by('id').first()
        if first is not None:
            first.delete()
    CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
