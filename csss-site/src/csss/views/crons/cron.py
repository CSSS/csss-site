from django.shortcuts import render

from csss.models import CronJob
from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_validate_digital_resources
from csss.views.context_creation.create_context_for_crons_html import create_context_for_crons_html
from csss.views.crons.process_specified_cron_request import process_specified_cron_request
from resource_management.views.gdrive_views import TAB_STRING

logger = get_logger()


def cron(request):
    """
        Shows the page where the user can add or update the cron timers and also trigger them
        """
    logger.info(f"[about/cron.py cron()] "
                f"request.POST={request.POST}")
    context = create_context_for_validate_digital_resources(request, tab=TAB_STRING)
    process_cron_request = request.method == "POST"
    cron_jobs = {
        cron_job.job_name: cron_job
        for cron_job in CronJob.objects.all()
    }
    if process_cron_request:
        return process_specified_cron_request(request, cron_jobs, context)
    create_context_for_crons_html(context, cron_jobs)
    return render(request, 'csss/crons/crons.html', context)
