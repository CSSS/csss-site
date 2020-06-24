import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .gdrive_views import create_google_drive_perms
from .github_views import create_github_perms
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from .resource_apis.github.github_api import GitHubAPI
from .views_helper import there_are_multiple_entries, verify_access_logged_user_and_create_context

logger = logging.getLogger('csss_site')

GOOGLE_DRIVE_KEY = 'gdrive'
GITHUB_KEY = 'github'
RESOURCES_KEY = 'resource'
TAB_STRING = 'administration'


def select_resource_to_manage(request):
    logger.info(f"[administration/resource_views.py select_resource_to_manage()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    return render(request, 'administration/resources/set_resources_access.html', context)


def manage_selected_resource(request):
    logger.info(f"[administration/resource_views.py manage_selected_resource()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    if RESOURCES_KEY in request.POST:
        if request.POST[RESOURCES_KEY] == GOOGLE_DRIVE_KEY:
            return HttpResponseRedirect("/administration/resources/gdrive/")
        if request.POST[RESOURCES_KEY] == GITHUB_KEY:
            return HttpResponseRedirect('/administration/resources/github')
    return render(request, 'administration/resources/invalid_resource_specified.html', context)


def validate_access(request):
    logger.info(f"[administration/resource_views.py validate_access()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    if there_are_multiple_entries(request.POST, RESOURCES_KEY):
        for resource in request.POST[RESOURCES_KEY]:
            logger.info(f"interpreting resource {resource}")
            if GOOGLE_DRIVE_KEY == resource:
                logger.info("user has selected to validate the access to the google drive")
                gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
                gdrive.ensure_root_permissions_are_correct(create_google_drive_perms())
            elif GITHUB_KEY == resource:
                logger.info("user has selected to validate the access to the google drive")
                github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
                github.ensure_proper_membership(create_github_perms())

    else:
        if request.POST[RESOURCES_KEY] == GOOGLE_DRIVE_KEY:
            logger.info("user has selected to validate the access to the google drive")
            gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
            gdrive.ensure_root_permissions_are_correct(create_google_drive_perms())
        if request.POST[RESOURCES_KEY] == GITHUB_KEY:
            logger.info("user has selected to validate the access to the google drive")
            github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
            github.ensure_proper_membership(create_github_perms())
    return HttpResponseRedirect('/administration/resources/select_resources')
