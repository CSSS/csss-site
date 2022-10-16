import importlib

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import BaseCommand

from csss.models import CronJob
from csss.setup_logger import get_logger


class Command(BaseCommand):

    def handle(self, **options):
        logger = get_logger(cron_module="cron_service", use_existing_logging=False)
        logger.info("setting up cron service")
        scheduler = BlockingScheduler()
        cron_jobs = CronJob.objects.all()
        # getattr(importlib.import_module("about.management.commands.test", package='CronJob'), "CronJob")
        # scheduler.add_job(
        #     func=the_class.theClass.cron_job_2, minutes=1, trigger='interval'
        # )
        for cron_job in cron_jobs:
            logger.info(f"[csss/cron_service.py cron()] adding job {cron_job.job_name} to the scheduler")
            scheduler.add_job(
                importlib.import_module('about.views.commands.nag_officers_to_enter_info').run_job)
        for cron_job in cron_jobs:
            logger.info(f"[csss/cron_service.py cron()] adding job {cron_job.job_name} to the scheduler")
            scheduler.add_job(
                importlib.import_module('about.views.commands.nag_officers_to_enter_info').run_job,
                args=[logger], trigger=CronTrigger.from_crontab(cron_job.schedule)
            )
            logger.info(f"[csss/cron_service.py cron()] job {cron_job.job_name} added to the scheduler")
        logger.info("starting cron service")
        scheduler.start()
