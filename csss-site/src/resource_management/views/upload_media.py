from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_main_context import create_main_context
from resource_management.views.create_context.create_context_for_upload_media_html import \
    create_context_for_upload_media_html
from resource_management.views.process_uploaded_media import process_uploaded_media


def upload_media(request):
    """
    Handles the page that deals with users who want to upload media from CSSS events
    """
    logger = Loggers.get_logger()
    logger.info("[resource_management/upload_media.py upload_media()] ")
    if request.method == "POST":
        return process_uploaded_media(request)
    else:
        context = create_main_context(request, 'documents')
        create_context_for_upload_media_html(context)
        return render(request, 'resource_management/upload_media.html', context)
