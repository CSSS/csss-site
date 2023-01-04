import datetime

from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_checking_google_drive_nags
from csss.views_helper import get_current_date
from resource_management.models import GoogleDriveFileAwaitingOwnershipChange, GoogleDriveRootFolderBadAccess
from resource_management.views.gdrive_views import TAB_STRING


def nags(request):
    """
    Displays the nags that have been done for the Google Drive files
    """
    logger = Loggers.get_logger()
    logger.info(f"[administration/nags.py nags()] request.POST={request.POST}")
    context = create_context_for_checking_google_drive_nags(request, tab=TAB_STRING)
    current_date = get_current_date() - datetime.timedelta(days=1)

    context.update({
        'ownership_changes': GoogleDriveFileAwaitingOwnershipChange.objects.all().filter(
            latest_date_check__gte=current_date
        ).order_by('file_owner'),
        'bad_accesses': GoogleDriveRootFolderBadAccess.objects.all().filter(
            latest_date_check__gte=current_date
        ).order_by('user')
    })
    return render(request, 'resource_management/nags.html', context)
