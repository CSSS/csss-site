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
    logger.info(f"[csss/cron_logs.py cron_logs()] request.POST={request.POST}")
    context = create_context_for_running_cron_jobs(request, tab=TAB_STRING)
    create_context_for_cron_logs_html(context, log_location=log_location)
    return render(request, 'csss/crons/cron_logs.html', context)
