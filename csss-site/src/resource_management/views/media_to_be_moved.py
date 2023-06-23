from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_checking_media_that_has_to_be_moved
from resource_management.models import MediaToBeMoved
from resource_management.views.gdrive_views import TAB_STRING


def media_to_be_moved(request):
    """
    Displays the media that has to be moved to the SFU Vault
    """
    logger = Loggers.get_logger()
    logger.info(f"[administration/nags.py nags()] request.POST={request.POST}")
    context = create_context_for_checking_media_that_has_to_be_moved(request, tab=TAB_STRING)

    context['medias_to_be_moved'] = MediaToBeMoved.objects.all().order_by('archive')
    return render(request, 'resource_management/medias_to_be_moved.html', context)
