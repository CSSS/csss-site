import importlib
import re

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from csss.models import CronJob
from csss.settings import URL_ROOT
from csss.views.context_creation.create_context_for_crons_html import create_context_for_crons_html
from csss.views.crons.Constants import CRON_JOB_MAPPING, CRON_JOB_UPDATE_ACTION_KEY, CRON_JOBS_SCHEDULES_KEY, \
    CRON_JOB_MAPPING_PATH_KEY, CRON_JOB_UPDATE_DETAILS_KEY
from csss.views.crons.save_or_update_cron_jobs import save_or_update_cron_jobs
from csss.views.crons.validators.validate_specified_cron_schedule import validate_specified_cron_schedule


def process_specified_cron_request(request, saved_cron_jobs_dict, context):
    """
    Takes in the user's existing Cron Jobs and validates the changes to the schedule before saving them
    or updates the database with the Cron Jobs outlined in the CRON_JOB_MAPPING.py
    or runs one of the cron jobs

    Keyword Argument:
    request -- the django request object
    saved_cron_jobs_dict -- a dictionary of the saved CronJobs where the key is the name and the value is the
     CronJob object itself
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error
    """
    request_dict = (parser.parse(request.POST.urlencode()))
    action = request_dict[CRON_JOB_UPDATE_ACTION_KEY]
    draft_cron_jobs = request_dict[CRON_JOBS_SCHEDULES_KEY]
    if re.compile("^run_job_").match(action) is not None:
        job_name = f"{action}".replace("run_job_", "")
        job_config = CRON_JOB_MAPPING[job_name]
        importlib.import_module(f"{job_config[CRON_JOB_MAPPING_PATH_KEY]}{job_name}").run_job(use_cron_logger=False)
        create_context_for_crons_html(
            context, saved_cron_jobs_dict, draft_cron_jobs=draft_cron_jobs
        )
        return render(request, 'csss/crons/crons.html', context)
    elif action == CRON_JOB_UPDATE_DETAILS_KEY:
        for cron_job_name, cron_job_info in CRON_JOB_MAPPING.items():
            if cron_job_name not in saved_cron_jobs_dict:
                CronJob(job_name=cron_job_name).save()
        for saved_cron_job in saved_cron_jobs_dict.values():
            if saved_cron_job.job_name not in CRON_JOB_MAPPING:
                saved_cron_job.cronjobrunstat_set.all().delete()
                saved_cron_job.delete()
        return HttpResponseRedirect(f"{URL_ROOT}cron")
    else:
        success, error_message = validate_specified_cron_schedule(draft_cron_jobs)
        if not success:
            create_context_for_crons_html(
                context, saved_cron_jobs_dict, error_messages=[error_message], draft_cron_jobs=draft_cron_jobs
            )
            return render(request, 'csss/crons/crons.html', context)
        save_or_update_cron_jobs(saved_cron_jobs_dict, draft_cron_jobs)
        return HttpResponseRedirect(f"{URL_ROOT}cron")
