import datetime
from time import perf_counter

from django.core.management.base import BaseCommand

from csss.models import CronJobRunStat, CronJob
from csss.setup_logger import Loggers
from resource_management.views.resource_views import validate_google_drive, validate_github

SERVICE_NAME = "validate_access"


class Command(BaseCommand):
    help = "validates the access for the google drive"

    def add_arguments(self, parser):
        parser.add_argument(
            '--google_drive',
            action="store_true",
            default=False,
            help="validates the access to the SFU CSSS Google Drive"
        )
        parser.add_argument(
            '--github',
            action="store_true",
            default=False,
            help="validates the access to the SFU CSSS GitHub "
        )

    def handle(self, *args, **options):
        time1 = perf_counter()
        current_date = datetime.datetime.now(date_timezone)
        logger = Loggers.get_logger(logger_name=SERVICE_NAME, current_date=current_date)
        logger.info(options)
        if options['google_drive']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to google drive")
            validate_google_drive()
        if options['github']:
            logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                        "to Github")
            validate_github()
        Loggers.remove_logger(SERVICE_NAME, current_date)
        time2 = perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()