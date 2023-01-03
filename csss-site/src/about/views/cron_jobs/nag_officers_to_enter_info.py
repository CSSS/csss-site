from subprocess import Popen

from about.management.commands.nag_officers_to_enter_info import SERVICE_NAME


def run_job():
    Popen(['python', 'manage.py', f'{SERVICE_NAME}'])
