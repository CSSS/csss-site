from subprocess import Popen

from django.conf import settings

from about.management.commands.nag_officers_to_enter_info import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
    else:
        Popen(['../../cron_scripts/prod_nag_officers_to_enter_info.sh'])
