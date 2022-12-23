import datetime
import importlib
from time import sleep

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import BaseCommand

from csss.models import CronJob
from csss.settings import CRON_SERVICE_NAME
from csss.setup_logger import Loggers, date_timezone
from csss.views.crons.Constants import CRON_JOB_MAPPING


class Command(BaseCommand):

    def handle(self, **options):
        seconds_in_an_hour = 60 * 60
        logger = Loggers.get_logger(logger_name=CRON_SERVICE_NAME, current_date=datetime.datetime.now(date_timezone))
        logger.info("[Cron_Service_Command handle()] setting up cron service")
        date = datetime.datetime.now(date_timezone)
        scheduler = BlockingScheduler()
        cron_jobs = [cron_job for cron_job in CronJob.objects.all() if cron_job.is_active]
        for cron_job in cron_jobs:
            logger.info(
                f"[Cron_Service_Command handle()] adding job {cron_job.job_name} with schedule of {cron_job.schedule}"
                " to the scheduler"
            )
            script_path = CRON_JOB_MAPPING[cron_job.job_name]['path']
            job = scheduler.add_job(
                importlib.import_module(f'{script_path}{cron_job.job_name}').run_job,
                trigger=CronTrigger.from_crontab(cron_job.schedule)
            )
            cron_job.job_id = job.id
            cron_job.save()
            logger.info(f"[Cron_Service_Command handle()] job {cron_job.job_name} added to the scheduler")
        logger.info("[Cron_Service_Command handle()] starting cron service")
        scheduler.start()
        logger.info("[Cron_Service_Command handle()] cron service started")
        while True:
            updated_cron_jobs = CronJob.objects.all().filter(last_update__gte=date)
            date = datetime.datetime.now(date_timezone)
            for updated_cron_job in updated_cron_jobs:
                job = scheduler.get_job(updated_cron_job.job_id)
                if updated_cron_job.schedule == "":
                    logger.info(
                        f"[Cron_Service_Command handle()] removing cron job {updated_cron_job.job_name} since the "
                        f"schedule is now empty "
                    )
                    scheduler.remove_job(job_id=job.id)
                    logger.info(f"[Cron_Service_Command handle()] cron job {updated_cron_job.job_name} removed")
                else:
                    logger.info(
                        f"[Cron_Service_Command handle()] updating cron job {updated_cron_job.job_name} "
                        f"with schedule of {updated_cron_job.schedule} from {job.trigger} to "
                        f"{updated_cron_job.schedule}"
                    )
                    script_path = CRON_JOB_MAPPING[updated_cron_job.job_name]['path']
                    scheduler.reschedule_job(
                        updated_cron_job.job_id,
                        importlib.import_module(f'{script_path}{updated_cron_job.job_name}').run_job,
                        trigger=CronTrigger.from_crontab(updated_cron_job.schedule)
                    )
                    logger.info(f"[Cron_Service_Command handle()] updated cron job {updated_cron_job.job_name} ")
            logger.info("[Cron_Service_Command handle()] going to sleep for an hour... ")
            sleep(seconds_in_an_hour)
