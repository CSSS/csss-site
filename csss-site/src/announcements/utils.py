from django.conf import settings
import datetime
import os


def get_settings():
    return {
        'attachment_upload_to': getattr(
            settings,
            'DJANGO_POST_ATTACHMENT_UPLOAD_TO',
            'announcement_attachments/%Y/%m/%d/'
        )
    }


def get_attachment_save_path(instance, filename):
    settings = get_settings()

    path = settings['attachment_upload_to']
    if '%' in path:
        path = datetime.datetime.utcnow().strftime(path)

    return os.path.join(
        path,
        filename,
    )
