from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from csss.views.crons.Constants import CRON_JOB_MAPPING


def create_context_for_cron_logs_html(context, error_messages=None, log_location=None, logs=None):
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    folders = [
        indx for indx, char in enumerate(log_location) if char == "/"
    ]
    context['parent_directory'] = f"/cron_logs{log_location[:log_location.rfind('/')]}" \
        if len(folders) > 1 \
        else f"/cron_logs"
    context['logs'] = logs
