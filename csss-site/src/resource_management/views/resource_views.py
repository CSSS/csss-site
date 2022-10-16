from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_current_and_past_officers_details
from csss.views.request_validation import validate_request_to_update_digital_resource_permissions
from csss.views_helper import there_are_multiple_entries
from .gdrive_views import create_google_drive_perms
from .github_views import create_github_perms
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from .resource_apis.github.github_api import GitHubAPI

GOOGLE_DRIVE_KEY = 'gdrive'
GITHUB_KEY = 'github'
RESOURCES_KEY = 'resource'
TAB_STRING = 'administration'

logger = get_logger()


def show_resources_to_validate(request):
    """
    Displays the resources that the user can validate
    """
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
    logger.info("[administration/resource_views.py determine_resource_to_validate()] interpreting resource"
                f" {selected_resource_to_validate}")
    if GOOGLE_DRIVE_KEY == selected_resource_to_validate:
        logger.info("[administration/resource_views.py determine_resource_to_validate()] user has selected"
                    " to validate the access to the google drive")
        validate_google_drive()
    if GITHUB_KEY == selected_resource_to_validate:
        logger.info("[administration/resource_views.py determine_resource_to_validate()] user has selected"
                    " to validate the access to the google drive")
        validate_github()


def validate_google_drive():
    """
    calls functions for validating google drive permissions
    """
    GoogleDrive().validate_ownerships_and_permissions(create_google_drive_perms())


def validate_github():
    """
    calls the functions for validating the github permissions
    """
    GitHubAPI().ensure_proper_membership(create_github_perms())
