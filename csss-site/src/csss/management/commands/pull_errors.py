import subprocess

from django.core.management import BaseCommand

from csss.models import CSSSError
from csss.setup_logger import Loggers

CRON_SERVICE_NAME = "pull_errors"


class Command(BaseCommand):

    def handle(self, **options):
        logger = Loggers.get_logger(logger_name=CRON_SERVICE_NAME)
        errors = CSSSError.objects.all()

        logger.info("download errors from PROD site")
        download_succeeded, download_failed = 0, 0
        for error in errors:
            exit_code, output = subprocess.getstatusoutput(
                f"mkdir -p {error.base_directory}/{error.file_path}; "
                f"scp csss@sfucsss.org:{error.get_prod_error_absolute_path} {error.get_error_absolute_path};"
            )
            if exit_code != 0:
                download_failed += 1
                logger.error(f"unable to download error file {error.get_error_absolute_path}")
            else:
                download_succeeded += 1
                logger.info(f"error file {error.get_error_absolute_path} download succeeded")
            exit_code, output = subprocess.getstatusoutput(
                f"scp csss@sfucsss.org:{error.get_prod_debug_absolute_path} {error.get_debug_absolute_path};"
            )
            if exit_code != 0:
                download_failed += 1
                logger.error(f"unable to download error file {error.get_debug_absolute_path}")
            else:
                download_succeeded += 1
                logger.info(f"error file {error.get_debug_absolute_path} download succeeded")
        logger.info(f"{download_failed} error file downloads failed")
        logger.info(f"{download_succeeded} error file downloads succeeded")
