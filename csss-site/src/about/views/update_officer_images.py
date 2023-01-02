from subprocess import Popen

from about.management.commands.update_officer_images import SERVICE_NAME


def run_job():
    Popen(['python', 'manage.py', f'{SERVICE_NAME}', '--download'])