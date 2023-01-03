from subprocess import Popen

from resource_management.management.commands.validate_github import SERVICE_NAME


def run_job():
    Popen(['python', 'manage.py', f'{SERVICE_NAME}', '--poll_email'])
