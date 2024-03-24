from subprocess import Popen

from django.conf import settings

from about.management.commands.nag_doa_to_generate_links import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
    else:
        process = Popen(['./about/cron_scripts/prod_nag_doa_to_generate_links.sh'])
    process.wait()
