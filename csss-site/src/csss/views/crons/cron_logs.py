import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_running_cron_jobs
from csss.views.context_creation.create_context_for_cron_logs_html import create_context_for_cron_logs_html
from resource_management.views.gdrive_views import TAB_STRING


def cron_logs(request, log_location):
    logger = get_logger()
    logger.info(f"[about/cron.py cron()] request.POST={request.POST}")
    file_path = f"{settings.LOG_LOCATION}{log_location}"
    context = create_context_for_running_cron_jobs(request, tab=TAB_STRING)
    if os.path.isdir(file_path):
        logs = os.listdir(file_path)
        if len(log_location) > 0 and log_location[-1:] == "/":
            log_location = log_location[:-1]
        logs = [f"{log_location}/{log}" for log in logs]
        logs.sort()
        logs = list(reversed(logs))
        create_context_for_cron_logs_html(context, log_location=log_location, logs=logs)
        return render(request, 'csss/crons/cron_logs.html', context)
    else:
        with open(f"{settings.LOG_LOCATION}{log_location}", 'rb') as a:
            return HttpResponse(a.read())
