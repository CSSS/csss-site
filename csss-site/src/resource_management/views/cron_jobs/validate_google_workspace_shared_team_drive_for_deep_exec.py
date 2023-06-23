from subprocess import Popen

from django.conf import settings

from resource_management.views.resource_apis.Constants import \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_DEEP_EXECS_SERVICE_NAME


def run_job():
    if settings.ENVIRONMENT == "LOCALHOST":
        process = Popen(['python', 'manage.py', f'{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_DEEP_EXECS_SERVICE_NAME}'])
    else:
        process = Popen(
            ['./resource_management/cron_scripts/prod_validate_google_workspace_shared_team_drive_for_deep_exec.sh']
        )
    process.wait()
