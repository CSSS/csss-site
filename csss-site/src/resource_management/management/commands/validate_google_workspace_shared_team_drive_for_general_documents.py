from django.core.management.base import BaseCommand

from csss.setup_logger import Loggers
from resource_management.views.resource_apis.Constants import \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME
from resource_management.views.resource_views import validate_google_workspace_shared_team_drive_for_general_documents


class Command(BaseCommand):
    help = "validates the access for the google drive"

    def handle(self, *args, **options):
        logger = Loggers.get_logger(logger_name=GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME)
        logger.info(options)
        logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                    "to google drive")
        validate_google_workspace_shared_team_drive_for_general_documents()
        Loggers.remove_logger(GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME)
