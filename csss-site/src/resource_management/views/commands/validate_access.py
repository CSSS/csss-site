from csss.setup_logger import get_or_setup_logger
from resource_management.views.resource_views import validate_google_drive, validate_github


def run_job():
    get_or_setup_logger(logger_name="cron_validate_access")
    validate_google_drive()
    validate_github()
