from subprocess import Popen

from django.conf import settings

from elections.management.commands.nag_election_officer_share_results import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
    else:
        process = Popen(['./elections/cron_scripts/nag_election_officer_share_results.sh'])
    process.wait()
