from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from csss.views.crons.Constants import CRON_JOB_MAPPING


def create_context_for_crons_html(context, cron_jobs, error_messages=None, draft_cron_jobs=None):
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    cron_mappings = {
        cron_job_name:
            {
                **cron_mapping,
                'active': cron_job_name in list(cron_jobs.keys()),
                "schedule": cron_jobs[cron_job_name].schedule
                if cron_job_name in cron_jobs else ""
            }
        for (cron_job_name, cron_mapping) in CRON_JOB_MAPPING.items()
    }
    if draft_cron_jobs is not None and type(draft_cron_jobs) is dict:
        for (job_name, schedule) in draft_cron_jobs.items():
            if job_name in list(CRON_JOB_MAPPING.keys()):
                cron_mappings[job_name]['schedule'] = schedule
    context['cron_mappings'] = list(cron_mappings.values())
