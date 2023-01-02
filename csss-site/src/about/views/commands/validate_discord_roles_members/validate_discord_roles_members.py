from subprocess import Popen

from about.management.commands.validate_discord_roles_members import SERVICE_NAME


def run_job():
    Popen(['python', 'manage.py', f'{SERVICE_NAME}'])