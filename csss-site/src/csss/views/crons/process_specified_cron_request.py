import importlib

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from csss.settings import URL_ROOT
from csss.views.context_creation.create_context_for_crons_html import create_context_for_crons_html
from csss.views.crons.Constants import CRON_JOB_MAPPING
from csss.views.crons.save_or_update_cron_jobs import save_or_update_cron_jobs
from csss.views.crons.validators.validate_specified_cron_schedule import validate_specified_cron_schedule


def process_specified_cron_request(request, cron_jobs, context):
    draft_cron_jobs = (parser.parse(request.POST.urlencode()))['cron_schedules']
    job_to_run = request.POST['job_to_run'] if 'job_to_run' in request.POST else None
    if job_to_run:
        job_config = CRON_JOB_MAPPING[job_to_run]
        importlib.import_module(f"{job_config['path']}{job_to_run}").run_job()
        create_context_for_crons_html(
            context, cron_jobs, draft_cron_jobs=draft_cron_jobs
        )
        return render(request, 'csss/crons/crons.html', context)
    else:
        success, error_message = validate_specified_cron_schedule(draft_cron_jobs)
        if not success:
            create_context_for_crons_html(
                context, cron_jobs, error_messages=[error_message], draft_cron_jobs=draft_cron_jobs
            )
            return render(request, 'csss/crons/crons.html', context)
        save_or_update_cron_jobs(cron_jobs, draft_cron_jobs)
        return HttpResponseRedirect(f"{URL_ROOT}cron")
