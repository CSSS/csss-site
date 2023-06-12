from subprocess import Popen

from django.conf import settings

from announcements.management.commands.process_announcements import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{SERVICE_NAME}', '--poll_email'])
    else:
        process = Popen(['./announcements/cron_scripts/prod_process_announcements.sh'])
    process.wait()
