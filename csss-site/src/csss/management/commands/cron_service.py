import importlib

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import BaseCommand

from csss.models import CronJob
from csss.setup_logger import Loggers
from csss.views.crons.Constants import CRON_JOB_MAPPING


class Command(BaseCommand):

    def handle(self, **options):
        logger = Loggers.get_logger(logger_name="cron_service")
        logger.info("[csss/cron_service.py cron()] setting up cron service")
        scheduler = BlockingScheduler()
        cron_jobs = CronJob.objects.all()
        for cron_job in cron_jobs:
            logger.info(f"[csss/cron_service.py cron()] adding job {cron_job.job_name} to the scheduler")
            script_path = CRON_JOB_MAPPING[cron_job.job_name]['path']
            scheduler.add_job(
                importlib.import_module(f'{script_path}{cron_job.job_name}').run_job,
                trigger=CronTrigger.from_crontab(cron_job.schedule)
            )
            logger.info(f"[csss/cron_service.py cron()] job {cron_job.job_name} added to the scheduler")
        logger.info("[csss/cron_service.py cron()] starting cron service")
        scheduler.start()
