from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from csss.views.crons.Constants import CRON_JOB_NAME_KEY, CRON_JOB_ACTIVE_KEY, CRON_JOB_SCHEDULE_KEY, \
    CRON_JOB_AVERAGE_RUN_TIME_KEY, CRON_JOB_CRON_MAPPINGS_KEY


def create_context_for_crons_html(context, saved_cron_jobs_dict, error_messages=None, draft_cron_jobs=None):
    """
    Populates the context dictionary that is used by
        csss/templates/csss/crons/crons.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the crons.html
    saved_cron_jobs_dict -- a dictionary of the saved CronJobs where the key is the name and the value is the
     CronJob object itself
    error_messages -- error message to display
    draft_cron_jobs -- the user updates for the cron jobs
    """
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)

    cron_mappings = {
        cron_job_name:
            {
                CRON_JOB_NAME_KEY: cron_job_name,
                CRON_JOB_ACTIVE_KEY: saved_cron_jobs_dict[cron_job_name].is_active,
                CRON_JOB_SCHEDULE_KEY: saved_cron_jobs_dict[cron_job_name].schedule
                if cron_job_name in saved_cron_jobs_dict else "",
                CRON_JOB_AVERAGE_RUN_TIME_KEY: saved_cron_jobs_dict[cron_job_name].get_average_run_time
            }
        for cron_job_name in saved_cron_jobs_dict.keys()
    }
    if draft_cron_jobs is not None and type(draft_cron_jobs) is dict:
        for (draft_cron_job_name, draft_cron_job_schedule) in draft_cron_jobs.items():
            cron_mappings[draft_cron_job_name][CRON_JOB_SCHEDULE_KEY] = draft_cron_job_schedule
    context[CRON_JOB_CRON_MAPPINGS_KEY] = list(cron_mappings.values())
