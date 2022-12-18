import os
import subprocess
import traceback

from django.conf import settings

from about.models import Officer
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.setup_logger import Loggers


def run_job(download=False, use_cron_logger=True, setup_website=False):
    remove_logger = False
    if use_cron_logger:
        logger = Loggers.get_logger(use_cron_logger=use_cron_logger)
    elif setup_website:
        logger = Loggers.get_logger()
    else:
        remove_logger = True
        logger = Loggers.get_logger(logger_name="update_officer_images")
    if download:
        os.system("rm -fr about/static/about_static/exec-photos")
        logger.info(f"[about/update_officer_images.py run_job()] now trying to download all the exec photos")
        officers_url = f"{settings.STAGING_SERVER}dev_csss_website_media/exec-photos/"
        retVal = os.system(
            f"wget -r -X '*' --no-host-directories {officers_url} -R "
            "'*html*' -P about/static/about_static/  --cut-dirs=1"
        )
        if retVal != 0:
            try:
                raise Exception(f"Unable to download the exec-photos from {officers_url}")
            except Exception:
                logger.error(traceback.format_exc())
                exit(1)
        logger.info(f"[about/update_officer_images.py run_job()] all exec-photos downloaded")
    for officer in Officer.objects.all().filter():
        officer.image = get_officer_image_path(officer.elected_term, officer.full_name)
        logger.info("[about/update_officer_images.py run_job()] "
                    f"officer_image_path = {officer.image}")
        officer.save()
    if remove_logger:
        Loggers.remove_logger(logger_name='update_officer_images')
