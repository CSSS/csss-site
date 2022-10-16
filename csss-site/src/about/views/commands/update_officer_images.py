import os

from django.conf import settings

from about.models import Officer
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.setup_logger import get_logger


def run_job(download=False):
    logger = get_logger()
    if download:
        os.system(
            "rm -fr about/static/about_static/exec-photos || true; "
            f"wget -r -X '*' --no-host-directories {settings.STAGING_SERVER}exec-photos/ -R "
            "'*html*' -P about/static/about_static/ || true"
        )
    for officer in Officer.objects.all().filter():
        officer.image = get_officer_image_path(officer.elected_term, officer.full_name)
        logger.info("[about/update_officer_images.py fix_image_for_officer()] "
                    f"officer_image_path = {officer.image}")
        officer.save()
