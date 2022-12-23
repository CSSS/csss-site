CRON_JOB_MAPPING_PATH_KEY = 'path'

CRON_JOB_MAPPING = {
    "nag_officers_to_enter_info": {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.commands."
    }, "update_discord_details": {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.commands.",
    }, "update_officer_images": {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.commands.",
    }, "validate_discord_roles_members": {
        CRON_JOB_MAPPING_PATH_KEY: "about.views.commands.validate_discord_roles_members.",
    }, "process_announcements": {
        CRON_JOB_MAPPING_PATH_KEY: "announcements.views.commands.process_announcements.",
    }, "validate_access": {
        CRON_JOB_MAPPING_PATH_KEY: "resource_management.views.commands.",
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
