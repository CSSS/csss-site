import logging

from django.core.management.base import BaseCommand

from resource_management.views.commands.validate_github import run_job as validate_github_validation_job

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "validates the access for the GitHub"

    def handle(self, *args, **options):
        logger.info(options)
        logger.info("[resource_management/validate_access.py handle()] user has selected to validate the access "
                    "to Github")
        validate_github_validation_job()
