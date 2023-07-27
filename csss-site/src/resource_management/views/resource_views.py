import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_current_and_past_officers_details
from csss.views.request_validation import validate_request_to_update_digital_resource_permissions
from csss.views_helper import there_are_multiple_entries
from .gdrive_views import create_google_drive_perms
from .github_views import create_github_perms
from .resource_apis.Constants import GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME, \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_DEEP_EXECS_SERVICE_NAME, \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_PUBLIC_GALLERY_SERVICE_NAME, \
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_PRIVATE_GALLERY_SERVICE_NAME, GITHUB_SERVICE_NAME
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from .resource_apis.github.github_api import GitHubAPI

GOOGLE_DRIVE_KEY = 'gdrive'
GITHUB_KEY = 'github'
RESOURCES_KEY = 'resource'
TAB_STRING = 'administration'


def show_resources_to_validate(request):
    """
    Displays the resources that the user can validate
    """
    logger = Loggers.get_logger()
    logger.info(f"[administration/resource_views.py show_resources_to_validate()] request.POST={request.POST}")
    return render(
        request,
        'resource_management/show_resources_for_validation.html',
        create_context_for_current_and_past_officers_details(request, tab=TAB_STRING)
    )


def validate_access(request):
    """
    takes in the inputs from the user on what resources to validate
    """
    logger = Loggers.get_logger()
    logger.info(f"[administration/resource_views.py validate_access()] request.POST={request.POST}")
    validate_request_to_update_digital_resource_permissions(request)
    if there_are_multiple_entries(request.POST, RESOURCES_KEY):
        for resource in request.POST[RESOURCES_KEY]:
            determine_resource_to_validate(resource)
    else:
        determine_resource_to_validate(request.POST[RESOURCES_KEY])
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/show_resources_for_validation')


def determine_resource_to_validate(selected_resource_to_validate):
    """
    determine which resource needs to be validated

    Keyword Arguments

    selected_resource_to_validate -- the resource the user has requested to validate

    """
    logger = Loggers.get_logger()
    logger.info("[administration/resource_views.py determine_resource_to_validate()] interpreting resource"
                f" {selected_resource_to_validate}")
    if GOOGLE_DRIVE_KEY == selected_resource_to_validate:
        logger.info("[administration/resource_views.py determine_resource_to_validate()] user has selected"
                    " to validate the access to the google drive")
        validate_google_workspace_shared_team_drive_for_general_documents()
    if GITHUB_KEY == selected_resource_to_validate:
        logger.info("[administration/resource_views.py determine_resource_to_validate()] user has selected"
                    " to validate the access to the google drive")
        validate_github()


def validate_google_workspace_shared_team_drive_for_general_documents():
    """
    calls functions for validating google drive permissions
    """
    time1 = time.perf_counter()
    GoogleDrive(
        settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS
    ).validate_ownerships_and_permissions(
        create_google_drive_perms(root_file_id=settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS)
    )
    time2 = time.perf_counter()
    total_seconds = time2 - time1
    cron_job = CronJob.objects.get(job_name=GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_GENERAL_DOCUMENTS_SERVICE_NAME)
    number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
    if len(number_of_stats) == 10:
        first = number_of_stats.order_by('id').first()
        if first is not None:
            first.delete()
    CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()


def validate_google_workspace_shared_team_drive_for_deep_exec():
    """
    calls functions for validating google drive permissions
    """
    time1 = time.perf_counter()
    GoogleDrive(
        settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC
    ).validate_ownerships_and_permissions(
        create_google_drive_perms(
            root_file_id=settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC,
            execs_only=True,
            relevant_previous_terms=0
        )
    )
    time2 = time.perf_counter()
    total_seconds = time2 - time1
    cron_job = CronJob.objects.get(job_name=GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_DEEP_EXECS_SERVICE_NAME)
    number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
    if len(number_of_stats) == 10:
        first = number_of_stats.order_by('id').first()
        if first is not None:
            first.delete()
    CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()


def validate_google_workspace_shared_team_drive_for_public_gallery():
    """
    calls functions for validating google drive permissions
    """
    time1 = time.perf_counter()
    GoogleDrive(
        settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY
    ).validate_ownerships_and_permissions(
        create_google_drive_perms(
            root_file_id=settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY
        )
    )
    time2 = time.perf_counter()
    total_seconds = time2 - time1
    cron_job = CronJob.objects.get(job_name=GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_PUBLIC_GALLERY_SERVICE_NAME)
    number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
    if len(number_of_stats) == 10:
        first = number_of_stats.order_by('id').first()
        if first is not None:
            first.delete()
    CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()


def validate_google_private_gallery_shared_team_drive():
    """
    calls functions for validating google drive permissions
    """
    time1 = time.perf_counter()
    GoogleDrive(
        settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY
    ).validate_ownerships_and_permissions(
        create_google_drive_perms(
            root_file_id=settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY
        )
    )
    time2 = time.perf_counter()
    total_seconds = time2 - time1
    cron_job = CronJob.objects.get(job_name=GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_PRIVATE_GALLERY_SERVICE_NAME)
    number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
    if len(number_of_stats) == 10:
        first = number_of_stats.order_by('id').first()
        if first is not None:
            first.delete()
    CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()


def validate_github():
    """
    calls the functions for validating the github permissions
    """
    time1 = time.perf_counter()
    GitHubAPI().ensure_proper_membership(create_github_perms())
    time2 = time.perf_counter()
    total_seconds = time2 - time1
    cron_job = CronJob.objects.get(job_name=GITHUB_SERVICE_NAME)
    number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
    if len(number_of_stats) == 10:
        first = number_of_stats.order_by('id').first()
        if first is not None:
            first.delete()
    CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
