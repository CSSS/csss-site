import os

from django.conf import settings

from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from csss.views.crons.Constants import PARENT_DIRECTORY_KEY, CRON_LOGS_BASE_URL_KEY, CRON_LOGS_DIRECTORY_KEY, \
    CRON_LOG_FILE_CONTENTS_KEY, CRON_LOGS_BASE_URL_KEY__HTML_NAME, CRON_JOBS_BASE_URL_KEY__HTML_NAME, \
    CRON_JOBS_BASE_URL_KEY, CRON_LOGS_FILE__HTML_NAME, CRON_LOGS_SIZE__HTML_NAME


def create_context_for_cron_logs_html(context, error_messages=None, log_location=None):
    """
    Populates the context dictionary that is used by
        csss/templates/csss/crons/cron_logs.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the cron_logs.html
    error_messages -- error message to display
    log_location -- part of the path that has to be displayed to the user, It's either a directory or a file.
    """
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)

    folders = [
        indx for indx, char in enumerate(log_location) if char == "/"
    ]
    context[PARENT_DIRECTORY_KEY] = f"/{CRON_LOGS_BASE_URL_KEY}"
    context[PARENT_DIRECTORY_KEY] += f"{log_location[:(log_location[:-1].rfind('/'))]}/" if len(folders) > 1 else "/"
    context[CRON_LOGS_BASE_URL_KEY__HTML_NAME] = CRON_LOGS_BASE_URL_KEY
    context[CRON_JOBS_BASE_URL_KEY__HTML_NAME] = CRON_JOBS_BASE_URL_KEY

    file_path = f"{settings.LOG_LOCATION}{log_location}"
    if os.path.isdir(file_path):
        if log_location[:1] != "/":
            log_location = f"/{log_location}"
        if log_location[:1] != "/":
            log_location = f"{log_location}/"
        front_end_log_location = log_location[1:] if log_location[:1] == "/" else log_location
        files = [
            {
                CRON_LOGS_FILE__HTML_NAME: f"{front_end_log_location}{log_file}/"
                if os.path.isdir(f"{settings.LOG_LOCATION}{log_location}{log_file}") else f"{front_end_log_location}{log_file}",
                CRON_LOGS_SIZE__HTML_NAME: round(os.stat(f"{file_path}/{log_file}").st_size)
            }
            for log_file in os.listdir(file_path)
        ]
        context[CRON_LOGS_DIRECTORY_KEY] = list(reversed(sorted(files, key=lambda x: x[CRON_LOGS_FILE__HTML_NAME])))
    else:
        context[CRON_LOG_FILE_CONTENTS_KEY] = open(f"{settings.LOG_LOCATION}{log_location}", 'rb').read().decode(
            "UTF-8")
