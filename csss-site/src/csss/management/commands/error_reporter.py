from time import sleep

from django.core.management import BaseCommand

from csss.Gmail import Gmail
from csss.models import CSSSError
from csss.setup_logger import Loggers
from csss.views.send_email import send_email

CRON_SERVICE_NAME = "error_reporter"


class Command(BaseCommand):

    def handle(self, **options):
        seconds_in_an_hour = 60 * 60
        logger = Loggers.get_logger(logger_name=CRON_SERVICE_NAME)
        while True:
            unprocessed_errors = CSSSError.objects.all().filter(processed=False)
            logger.info(f"[csss/error_reporter.py handle()] detected {len(unprocessed_errors)} unprocessed_error")
            for unprocessed_error in unprocessed_errors:
                unprocessed_error.processed = True
            CSSSError.objects.bulk_update(unprocessed_errors, ['processed'])
            logger.info("[csss/error_reporter.py handle()] any unprocessed errors updated to \"processed\"")
            processed_files = []
            if len(unprocessed_errors) > 0:
                logger.info("[csss/error_reporter.py handle()] connecting to gmail")
                gmail = Gmail()
                for unprocessed_error in unprocessed_errors:
                    if unprocessed_error.get_error_absolute_path not in processed_files:
                        logger.info(
                            "[csss/error_reporter.py handle()] emailing the sys-admin about errors in "
                            f"{unprocessed_error.get_error_absolute_path}"
                        )
                        message = f"Error in {unprocessed_error.filename}"
                        send_email(
                            f"{unprocessed_error.file_path} ERRORS detected in CSSS-WEBSITE", message,
                            "csss-sysadmin@sfu.ca", "Jace",
                            gmail=gmail, attachment=unprocessed_error.get_error_absolute_path
                        )
                        logger.info("[csss/error_reporter.py handle()] sys-admin emailed about above error.")
                        processed_files.append(unprocessed_error.get_error_absolute_path)
                gmail.close_connection()
                logger.info("[csss/error_reporter.py handle()] disconnected from gmail")
            logger.info("[csss/error_reporter.py handle()] going to sleep for an hour")
            sleep(seconds_in_an_hour)
