from subprocess import Popen

from about.management.commands.update_discord_details import SERVICE_NAME


def run_job():
    Popen(['python', 'manage.py', f'{SERVICE_NAME}'])