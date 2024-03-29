from subprocess import Popen

from django.conf import settings

from elections.management.commands.remind_election_officer_to_provide_websurvey_link import SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
    else:
        process = Popen(['./elections/cron_scripts/remind_election_officer_to_provide_websurvey_link.sh'])
    process.wait()
