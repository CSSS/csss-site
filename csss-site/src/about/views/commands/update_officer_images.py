import os
import traceback

from django.conf import settings

from about.models import Officer
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.setup_logger import Loggers


def update_officer_images(download=False):
    logger = Loggers.get_logger()
    if download:
        if settings.ENVIRONMENT == "LOCALHOST":
            os.system("rm -fr about/static/about_static/exec-photos")
        logger.info("[about/update_officer_images.py run_job()] now trying to download all the exec photos")
        
        if settings.ENVIRONMENT == "LOCALHOST":
            officers_url = f"{settings.STAGING_SERVER}dev_csss_website_media/exec-photos/"
            ret_val = os.system(
                f"wget -r -X '*' --no-host-directories {officers_url} -R "
                "'*html*' -P about/static/about_static/  --cut-dirs=1"
            )
        else:
            ret_val = os.system("cd /mnt/csss_website_media/csss-site-exec-photos && git pull")
        if ret_val != 0:
            try:
                raise Exception(f"Unable to download the exec-photos from {officers_url}")
            except Exception:
                logger.error(traceback.format_exc())
                return
        logger.info("[about/update_officer_images.py run_job()] all exec-photos downloaded")
    for officer in Officer.objects.all().filter():
        officer.image = get_officer_image_path(officer.elected_term, officer.full_name)
        logger.info("[about/update_officer_images.py run_job()] "
                    f"officer_image_path = {officer.image}")
        officer.save()
