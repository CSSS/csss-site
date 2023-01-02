import datetime
import time

from django.core.management.base import BaseCommand

from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers, date_timezone
from resource_management.views.resource_views import validate_google_drive

SERVICE_NAME = "validate_google_drive"


class Command(BaseCommand):
    help = "validates the access for the google drive"

    def handle(self, *args, **options):
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        logger.info(options)
        logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                    "to google drive")
        time1 = time.perf_counter()
        current_date = datetime.datetime.now(date_timezone)
        validate_google_drive()
        time2 = time.perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
        Loggers.remove_logger(SERVICE_NAME, current_date)
