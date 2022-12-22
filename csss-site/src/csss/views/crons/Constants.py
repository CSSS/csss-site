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

CRON_BASE_URL_KEY = "cron_logs"

CRON_LOG_FILE_CONTENTS_KEY = 'log'
CRON_LOGS_DIRECTORY_KEY = f'{CRON_LOG_FILE_CONTENTS_KEY}s'

CRON_JOB_NAME_KEY = 'job_name'
CRON_JOB_ACTIVE_KEY = 'active'
CRON_JOB_SCHEDULE_KEY = 'schedule'
CRON_JOB_LOGS_EXIST_KEY = 'logs_exist'
CRON_JOB_AVERAGE_RUN_TIME_KEY = 'average_run_time'
CRON_JOB_CRON_MAPPINGS_KEY = 'cron_mappings'

CRON_JOB_UPDATE_ACTION_KEY = 'action'

CRON_JOBS_SCHEDULES_KEY = 'cron_schedules'

CRON_JOB_UPDATE_DETAILS_KEY = 'update_cron_job_details'
