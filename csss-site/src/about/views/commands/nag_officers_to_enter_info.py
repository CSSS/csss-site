import datetime
import time

from about.models import UnProcessedOfficer, Officer
from about.views.input_new_officers.specify_new_officers.notifications. \
    send_notification_asking_officer_to_fill_in_form import \
    send_notification_asking_officer_to_fill_in_form
from csss.models import CronJobRunStat, CronJob
from csss.setup_logger import Loggers, date_timezone
from csss.views.send_discord_dm import send_discord_dm

SERVICE_NAME = "nag_officers_to_enter_info"


def run_job():
    time1 = time.perf_counter()
    current_date = datetime.datetime.now(date_timezone)
    logger = Loggers.get_logger(logger_name=SERVICE_NAME, current_date=current_date)
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all()
    for unprocessed_officer in unprocessed_officers:
        success, error_message = send_notification_asking_officer_to_fill_in_form(
            unprocessed_officer.discord_id,
            unprocessed_officer.full_name,
            officers.filter(sfu_computing_id=unprocessed_officer.sfu_computing_id).first() is None
        )
        unprocessed_officer.number_of_nags += 1
        unprocessed_officer.save()
        if (unprocessed_officer.number_of_nags % 3) == 0:
            send_discord_dm(
                '288148680479997963', "unfilled in officer data",
                f"{unprocessed_officer.full_name} still has not filled in their data..."
            )
        logger.info(
            f"[about/nag_officers_to_enter_info.py()] {'nagged ' if success else 'was not able to nag '}"
            f"{unprocessed_officer.full_name} to fill in their info"
            f"{'' if success else f' due to error {error_message}'}."
        )
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
