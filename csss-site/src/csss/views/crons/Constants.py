from about.management.commands.nag_officers_to_enter_info import \
    SERVICE_NAME as NAG_OFFICERS_TO_ENTER_INFO_AS_SERVICE_NAME
from about.management.commands.update_discord_details \
    import SERVICE_NAME as UPDATE_DISCORD_DETAILS_SERVICE_NAME
from about.management.commands.update_officer_images \
    import SERVICE_NAME as UPDATE_OFFICER_IMAGES_SERVICE_NAME
from about.management.commands.validate_discord_roles_members \
    import SERVICE_NAME as VALIDATE_DISCORD_ROLES_MEMBERS_SERVICE_NAME
from announcements.management.commands.process_announcements \
    import SERVICE_NAME as PROCESS_ANNOUNCEMENTS_SERVICE_NAME
from elections.management.commands.nag_election_officer_share_results \
    import SERVICE_NAME as NAG_ELECTION_OFFICERS_SERVICE_NAME
from resource_management.views.resource_apis.Constants import \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME, \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_DEEP_EXECS_SERVICE_NAME, \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_PUBLIC_GALLERY_SERVICE_NAME, GITHUB_SERVICE_NAME

CRON_JOB_MAPPING_PATH_KEY = 'path'

CRON_JOB_MAPPING = {
    NAG_OFFICERS_TO_ENTER_INFO_AS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.cron_jobs."
    }, UPDATE_DISCORD_DETAILS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.cron_jobs.",
    }, UPDATE_OFFICER_IMAGES_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.cron_jobs.",
    }, VALIDATE_DISCORD_ROLES_MEMBERS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.cron_jobs.",
    }, PROCESS_ANNOUNCEMENTS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "announcements.views.cron_jobs.",
    }, NAG_ELECTION_OFFICERS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "elections.views.cron_jobs.",
    }, GITHUB_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "resource_management.views.cron_jobs.",
    }, GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "resource_management.views.cron_jobs.",
    }, GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_DEEP_EXECS_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "resource_management.views.cron_jobs.",
    }, GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_PUBLIC_GALLERY_SERVICE_NAME: {
        CRON_JOB_MAPPING_PATH_KEY: "resource_management.views.cron_jobs.",
    }
}
PARENT_DIRECTORY_KEY = "parent_directory"

CRON_LOGS_BASE_URL_KEY__HTML_NAME = "cron_logs_base_url_key__html_name"
CRON_LOGS_BASE_URL_KEY = "cron_logs"
CRON_JOBS_BASE_URL_KEY__HTML_NAME = "cron_base_url_key__html_name"
CRON_JOBS_BASE_URL_KEY = "cron"

CRON_LOG_FILE_CONTENTS_KEY = 'log_file'
CRON_LOGS_DIRECTORY_KEY = 'log_files'

CRON_LOGS_FILE__HTML_NAME = 'file'
CRON_LOGS_SIZE__HTML_NAME = 'size'

CRON_JOB_NAME_KEY = 'job_name'
CRON_JOB_ACTIVE_KEY = 'active'
CRON_JOB_SCHEDULE_KEY = 'schedule'
CRON_JOB_AVERAGE_RUN_TIME_KEY = 'average_run_time'
CRON_JOB_CRON_MAPPINGS_KEY = 'cron_mappings'

CRON_JOB_UPDATE_ACTION_KEY = 'action'

CRON_JOBS_SCHEDULES__HTML_NAME = 'cron_job_schedules__html_name'
CRON_JOBS_SCHEDULES_KEY = 'cron_schedules'

CRON_JOB_UPDATE_DETAILS_KEY = 'update_cron_job_details'

CRON_JOBS_ACTION_BUTTON_NAME__HTML_NAME = 'cron_jobs_action_button_name__html_name'

RUN_JOB__ACTION_ID_PREFIX = "run_job_"
RUN_JOB_ACTION__HTML_NAME = 'run_job_action__html_name'

UPDATE_CRON_SCHEDULE__HTML_NAME = 'update_cron_schedule__html_name'
UPDATE_CRON_SCHEDULE__VALUE = 'update_cron_schedule'
UPDATE_CRON_JOB_DETAILS__HTML_NAME = 'update_cron_job_details__html_name'
UPDATE_CRON_JOB_DETAILS__VALUE = 'update_cron_job_details'
