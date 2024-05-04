import time
from time import sleep

from django.core.management import BaseCommand

from about.models import UnProcessedOfficer, Officer
from about.views.input_new_officers.specify_new_officers.notifications.\
    send_notification_asking_officer_to_fill_in_form import \
    send_notification_asking_officer_to_fill_in_form
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers

SERVICE_NAME = "nag_officers_to_enter_info"


class Command(BaseCommand):
    help = "nag any officers who have not entered their info"

    def handle(self, *args, **options):
        time1 = time.perf_counter()
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all()
        for unprocessed_officer in unprocessed_officers:
            sleep(1)
            unprocessed_officer.number_of_nags += 1
            unprocessed_officer.save()
            first_time_officer = (
                officers.filter(sfu_computing_id=unprocessed_officer.sfu_computing_id).first() is None
            )
            success, error_message = send_notification_asking_officer_to_fill_in_form(
                unprocessed_officer.discord_id, unprocessed_officer.full_name, first_time_officer)
            if not success:
                logger.error(f"[about/nag_officers_to_enter_info.py()] {error_message}")
            logger.info(
                f"[about/nag_officers_to_enter_info.py()] reminded {unprocessed_officer.full_name} to fill in"
                f" their info"
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
