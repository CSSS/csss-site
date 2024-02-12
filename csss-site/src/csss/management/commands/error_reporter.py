import re
from time import sleep

from django.core.management import BaseCommand

from csss.models import CSSSError
from csss.setup_logger import Loggers
from csss.views.create_github_issue import create_github_issue

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
                for unprocessed_error in unprocessed_errors:
                    if unprocessed_error.get_error_absolute_path not in processed_files:
                        logger.info(
                            "[csss/error_reporter.py handle()] will create github issues errors in "
                            f"{unprocessed_error.get_error_absolute_path}"
                        )
                        with open(unprocessed_error.get_error_absolute_path, 'r') as f:
                            f.seek(0)
                            error_lines = []
                            error_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} = ERROR = ")
                            non_error_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} = (INFO|DEBUG) = ")
                            error_encountered = False
                            log_issue = False
                            f.flush()
                            lines = f.readlines()
                            logger.info("[csss/error_reporter.py handle()] reading through file "
                                        f"{unprocessed_error.get_error_absolute_path}")
                            for line in lines:
                                if error_pattern.match(line):
                                    error_encountered = True
                                    error_lines.append(line)
                                elif non_error_pattern.match(line) and error_encountered:
                                    log_issue = True
                                elif error_encountered:
                                    error_lines.append(line)
                                elif non_error_pattern.match(line):
                                    pass
                                else:
                                    pass
                                if log_issue:
                                    log_issue = False
                                    error_encountered = False
                                    create_github_issue(error_lines)
                                    logger.info(
                                        "[csss/error_reporter.py handle()] github issue created about above error."
                                    )
                                    error_lines.clear()
                            if log_issue or error_encountered:
                                create_github_issue(error_lines)
                                logger.info(
                                    "[csss/error_reporter.py handle()] github issue created about above error."
                                )
                                error_lines.clear()
                        processed_files.append(unprocessed_error.get_error_absolute_path)
            logger.info("[csss/error_reporter.py handle()] going to sleep for an hour")
            sleep(seconds_in_an_hour)
