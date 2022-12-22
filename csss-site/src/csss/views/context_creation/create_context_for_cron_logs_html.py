import os

from django.conf import settings

from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from csss.views.crons.Constants import PARENT_DIRECTORY_KEY, CRON_BASE_URL_KEY, CRON_LOGS_DIRECTORY_KEY, \
    CRON_LOG_FILE_CONTENTS_KEY


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
    context[PARENT_DIRECTORY_KEY] = f"/{CRON_BASE_URL_KEY}"
    context[PARENT_DIRECTORY_KEY] += f"{log_location[:(log_location[:-1].rfind('/'))]}/" if len(folders) > 1 else f"/"

    file_path = f"{settings.LOG_LOCATION}{log_location}"
    if os.path.isdir(file_path):
        if log_location[:1] == "/":
            log_location = log_location[1:]
        files = [
            {
                "file": f"{log_location}{log_file}/" if os.path.isdir(f"{settings.LOG_LOCATION}/{log_file}") else f"{log_location}{log_file}",
                "size": round(os.stat(f"{file_path}/{log_file}").st_size / 1000)
            }
            for log_file in os.listdir(file_path)
        ]
        context[CRON_LOGS_DIRECTORY_KEY] = list(reversed(sorted(files, key=lambda x: x['file'])))
    else:
        context[CRON_LOG_FILE_CONTENTS_KEY] = open(f"{settings.LOG_LOCATION}{log_location}", 'rb').read().decode(
            "UTF-8").replace("\n", "<br>")
