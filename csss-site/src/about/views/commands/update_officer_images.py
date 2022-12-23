import datetime
import os
import time
import traceback

from django.conf import settings

from about.management.commands.update_officer_images import SERVICE_NAME
from about.models import Officer
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers, date_timezone


def run_job(download=False, setup_website=False):
    time1 = time.perf_counter()
    remove_logger = False
    current_date = datetime.datetime.now(date_timezone)
    if setup_website:
        logger = Loggers.get_logger()
    else:
        remove_logger = True
        logger = Loggers.get_logger(logger_name=SERVICE_NAME, current_date=current_date)
    if download:
        os.system("rm -fr about/static/about_static/exec-photos")
        logger.info("[about/update_officer_images.py run_job()] now trying to download all the exec photos")
        officers_url = f"{settings.STAGING_SERVER}dev_csss_website_media/exec-photos/"
        ret_val = os.system(
            f"wget -r -X '*' --no-host-directories {officers_url} -R "
            "'*html*' -P about/static/about_static/  --cut-dirs=1"
        )
        if ret_val != 0:
            try:
                raise Exception(f"Unable to download the exec-photos from {officers_url}")
            except Exception:
                logger.error(traceback.format_exc())
                exit(1)
        logger.info("[about/update_officer_images.py run_job()] all exec-photos downloaded")
    for officer in Officer.objects.all().filter():
        officer.image = get_officer_image_path(officer.elected_term, officer.full_name)
        logger.info("[about/update_officer_images.py run_job()] "
                    f"officer_image_path = {officer.image}")
        officer.save()
    if remove_logger:
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
