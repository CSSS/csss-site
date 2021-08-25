import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views.request_validation import validate_request_to_manage_digital_resource_permissions
from csss.views_helper import there_are_multiple_entries, create_context_for_officers
from .gdrive_views import create_google_drive_perms
from .github_views import create_github_perms
from .gitlab_views import create_gitlab_perms
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from .resource_apis.github.github_api import GitHubAPI
from .resource_apis.gitlab.gitlab_api import GitLabAPI

logger = logging.getLogger('csss_site')

GOOGLE_DRIVE_KEY = 'gdrive'
GITHUB_KEY = 'github'
SFU_GITLAB_KEY = 'gitlab'
RESOURCES_KEY = 'resource'
TAB_STRING = 'administration'


def show_resources_to_validate(request):
    """
    Displays the resources that the user can validate
    """
    logger.info(f"[administration/resource_views.py show_resources_to_validate()] request.POST={request.POST}")
    html_page = 'resource_management/show_resources_for_validation.html'
    validate_request_to_manage_digital_resource_permissions(request, html=html_page)
    context = create_context_for_officers(request, TAB_STRING)
    return render(request, html_page, context)


def validate_access(request):
    """
    takes in the inputs from the user on what resources to validate
    """
    logger.info(f"[administration/resource_views.py validate_access()] request.POST={request.POST}")
    endpoint = f'{settings.URL_ROOT}resource_management/show_resources_for_validation'
    validate_request_to_manage_digital_resource_permissions(request, endpoint=endpoint)
    if there_are_multiple_entries(request.POST, RESOURCES_KEY):
        for resource in request.POST[RESOURCES_KEY]:
            determine_resource_to_validate(resource)
    else:
        determine_resource_to_validate(request.POST[RESOURCES_KEY])
    return HttpResponseRedirect(endpoint)


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
    if SFU_GITLAB_KEY == selected_resource_to_validate:
        logger.info("[administration/resource_views.py determine_resource_to_validate()] user has selected"
                    " to validate the access to the SFU Gitlab")
        validate_sfu_gitlab()


def validate_google_drive():
    """
    calls functions for validating google drive permissions
    """
    GoogleDrive(
        settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID
    ).validate_ownerships_and_permissions(create_google_drive_perms())


def validate_github():
    """
    calls the functions for validating the github permissions
    """
    GitHubAPI(
        settings.GITHUB_ACCESS_TOKEN
    ).ensure_proper_membership(create_github_perms())


def validate_sfu_gitlab():
    """
    calls the functions for validating the sfu gitlab permissions
    """
    GitLabAPI(
        settings.GITLAB_PRIVATE_TOKEN
    ).ensure_proper_membership(create_gitlab_perms())
