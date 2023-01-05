from subprocess import Popen

from django.conf import settings

from resource_management.management.commands.validate_google_drive import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
    else:
        Popen(['./resource_management/cron_scripts/prod_validate_google_drive.sh'])
