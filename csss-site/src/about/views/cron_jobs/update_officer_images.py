from subprocess import Popen

from django.conf import settings

from about.management.commands.update_officer_images import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{SERVICE_NAME}', '--download'])
    else:
        process = Popen(['./about/cron_scripts/prod_update_officer_images.sh'])
    process.wait()
