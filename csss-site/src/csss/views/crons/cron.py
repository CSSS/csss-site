from django.shortcuts import render

from csss.models import CronJob
from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_running_cron_jobs
from csss.views.context_creation.create_context_for_crons_html import create_context_for_crons_html
from csss.views.crons.process_specified_cron_request import process_specified_cron_request
from resource_management.views.gdrive_views import TAB_STRING


def cron(request):
    """
    Shows the page where the user can add or update the cron timers and also trigger them
    """
    logger = Loggers.get_logger()
    logger.info(f"[about/cron.py cron()] request.POST={request.POST}")
    context = create_context_for_running_cron_jobs(request, tab=TAB_STRING)
    process_cron_request = request.method == "POST"
    saved_cron_jobs_dict = {
        cron_job.job_name: cron_job
        for cron_job in CronJob.objects.all().order_by('id')
    }
    if process_cron_request:
        return process_specified_cron_request(request, saved_cron_jobs_dict, context)
    create_context_for_crons_html(context, saved_cron_jobs_dict)
    return render(request, 'csss/crons/crons.html', context)
