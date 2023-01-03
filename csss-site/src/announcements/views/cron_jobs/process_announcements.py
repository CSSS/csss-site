import logging
from subprocess import Popen

from announcements.management.commands.process_announcements import SERVICE_NAME

logger = logging.getLogger('csss_site')


def run_job():
    Popen(['python', 'manage.py', f'{SERVICE_NAME}', '--poll_email'])
