import os

from django.conf import settings

from about.models import Officer
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.setup_logger import get_or_setup_logger, get_logger


def run_job(download=False):

    # this is necessary because this might have been called as part of the
    # setup_website command which means it should use the logger that's already been created
    try:
        logger = get_logger()
    except Exception as e:
        if e == "Could not find a logger":
            logger = get_or_setup_logger(logger_name="update_officer_images")
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
