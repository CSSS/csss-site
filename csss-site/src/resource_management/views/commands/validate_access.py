from csss.setup_logger import Loggers
from resource_management.views.resource_views import validate_google_drive, validate_github


def run_job(use_cron_logger=True):
    Loggers.get_logger(logger_name="cron_validate_access", use_cron_logger=use_cron_logger)
    validate_google_drive()
    validate_github()
    Loggers.remove_logger(logger_name="cron_validate_access")
