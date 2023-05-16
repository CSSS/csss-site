from subprocess import Popen

from django.conf import settings

from about.management.commands.validate_discord_roles_members import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
    else:
        process = Popen(['./about/cron_scripts/prod_validate_discord_roles_members.sh'])
    process.wait()
