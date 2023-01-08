from time import sleep

from django.core.management import BaseCommand

from csss.Gmail import Gmail
from csss.models import Error
from csss.setup_logger import Loggers
from csss.views.send_email import send_email

CRON_SERVICE_NAME = "error_reporter"


class Command(BaseCommand):

    def handle(self, **options):
        seconds_in_an_hour = 60 * 60
        logger = Loggers.get_logger(logger_name=CRON_SERVICE_NAME)
        while True:
            unprocessed_errors = Error.objects.all().filter(processed=False)
            logger.info(f"[csss/error_reporter.py handle()] detected {len(unprocessed_errors)} unprocessed_error")
            for unprocessed_error in unprocessed_errors:
                unprocessed_error.processed = True
            Error.objects.bulk_update(unprocessed_errors, ['processed'])
            logger.info("[csss/error_reporter.py handle()] any unprocessed errors updated to \"processed\"")
            if len(unprocessed_errors) > 0:
                logger.info("[csss/error_reporter.py handle()] connecting to gmail")
                gmail = Gmail()
                for unprocessed_error in unprocessed_errors:
                    logger.info(
                        "[csss/error_reporter.py handle()] emailing the sys-admin about error "
                        f"{unprocessed_error.message}"
                    )
                    message = f"{unprocessed_error.level} {unprocessed_error.message} in {unprocessed_error.filename}"
                    send_email(
                        "ERRORS detected in CSSS-WEBSITE", message, "csss-sysadmin@sfu.ca", "Jace",
                        gmail=gmail, attachment=unprocessed_error.filename
                    )
                    logger.info("[csss/error_reporter.py handle()] sys-admin emailed about above error.")
                gmail.close_connection()
                logger.info("[csss/error_reporter.py handle()] disconnected from gmail")
            logger.info("[csss/error_reporter.py handle()] going to sleep for an hour")
            sleep(seconds_in_an_hour)
