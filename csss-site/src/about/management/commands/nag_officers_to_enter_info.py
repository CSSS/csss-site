import time
from time import sleep

from django.core.management import BaseCommand

from about.models import UnProcessedOfficer, Officer
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers
from csss.views.send_discord_dm import send_discord_dm

SERVICE_NAME = "nag_officers_to_enter_info"


class Command(BaseCommand):
    help = "nag any officers who have not entered their info"

    def handle(self, *args, **options):
        time1 = time.perf_counter()
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        unprocessed_officers = UnProcessedOfficer.objects.all()
        current_director_of_archives = Officer.objects.all().filter(
            position_name='Director of Archives'
        ).order_by('-start_date').first()
        current_systems_admin = Officer.objects.all().filter(
            position_name='Systems Administrator'
        ).order_by('-start_date').first()
        for unprocessed_officer in unprocessed_officers:
            sleep(1)
            unprocessed_officer.number_of_nags += 1
            unprocessed_officer.save()
            if (unprocessed_officer.number_of_nags % 3) == 0:
                send_discord_dm(
                    current_systems_admin.discord_id, "unfilled in officer data",
                    f"{unprocessed_officer.full_name} still has not filled in their data..."
                )
            if current_director_of_archives is not None:
                send_discord_dm(
                    current_director_of_archives.discord_id, "unfilled in officer data",
                    f"{unprocessed_officer.full_name} still has not filled in their data..."
                )
            logger.info(
                f"[about/nag_officers_to_enter_info.py()] alerted the Sys Admin and DoA that "
                f"{unprocessed_officer.full_name} has not filled in their info"
            )
        time2 = time.perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
        Loggers.remove_logger(SERVICE_NAME)
