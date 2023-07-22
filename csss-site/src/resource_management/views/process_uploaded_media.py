import datetime
import re

from django.http import HttpResponseRedirect

from csss.settings import URL_ROOT
from csss.views.send_email import send_email
from resource_management.models import Upload, MediaUpload
from resource_management.views.Constants import MEDIA_UPLOADS__HTML_NAME, MEDIA_UPLOADS_NOTE__HTML_NAME, \
    MEDIA_UPLOADS_EVENT_TYPE__HTML_NAME, MEDIA_UPLOADS_EVENT_DATE__HTML_NAME, \
    MEDIA_UPLOADS_EVENT_TYPE_SPECIFIER__HTML_NAME


def process_uploaded_media(request):
    """
    Process the request to upload media from a CSSS event
    """
    media_uploaded = (
        request.FILES.get(MEDIA_UPLOADS__HTML_NAME, None) is not None  # if the user uploaded some media
        or
        (
            request.POST[MEDIA_UPLOADS_NOTE__HTML_NAME] != "" and
            re.match(r"https://drive.google.com/drive/folders/[a-zA-Z0-9_]",
                     request.POST[MEDIA_UPLOADS_NOTE__HTML_NAME])
         )
        # if the user just added a note that is a google drive link
    )
    if media_uploaded:
        upload_has_specifier = request.POST[MEDIA_UPLOADS_EVENT_TYPE__HTML_NAME] == 'Other'
        event_type_specifier = request.POST[MEDIA_UPLOADS_EVENT_TYPE_SPECIFIER__HTML_NAME] \
            if upload_has_specifier else None
        upload = Upload(
            upload_date=datetime.datetime.now(),
            event_type=request.POST[MEDIA_UPLOADS_EVENT_TYPE__HTML_NAME],
            event_date=request.POST[MEDIA_UPLOADS_EVENT_DATE__HTML_NAME],
            relevant_note=request.POST[MEDIA_UPLOADS_NOTE__HTML_NAME],
            event_type_specifier=event_type_specifier
        )
        upload.save()
        if request.FILES.get(MEDIA_UPLOADS__HTML_NAME, None) is not None:
            for media_upload in (dict(request.FILES))[MEDIA_UPLOADS__HTML_NAME]:
                media_upload_obj = MediaUpload(media_upload)
                media_upload_obj.upload = upload
                media_upload_obj.save()
        send_email(
            f"new media upload for {upload.event_type}",
            f"got {len(upload.mediaupload_set.all())} new uploads for {upload}",
            "csss-sysadmin@sfu.ca",
            'jace'
        )
    return HttpResponseRedirect(f"{URL_ROOT}resource_management/upload")
