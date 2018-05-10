from django.conf import settings
import datetime
import os

def get_settings():
    return {
        'strip_unallowed_mimetypes': getattr(
            settings,
            'DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES',
            False
        ),
        'allowed_mimetypes': getattr(
            settings,
            'DJANGO_MAILBOX_ALLOWED_MIMETYPES',
            [
                'text/plain',
                'text/html'
            ]
        ),
        'text_stored_mimetypes': getattr(
            settings,
            'DJANGO_MAILBOX_TEXT_STORED_MIMETYPES',
            [
                'text/plain',
                'text/html'
            ]
        ),
        'altered_message_header': getattr(
            settings,
            'DJANGO_MAILBOX_ALTERED_MESSAGE_HEADER',
            'X-Django-Mailbox-Altered-Message'
        ),
        'attachment_interpolation_header': getattr(
            settings,
            'DJANGO_MAILBOX_ATTACHMENT_INTERPOLATION_HEADER',
            'X-Django-Mailbox-Interpolate-Attachment'
        ),
        'attachment_upload_to': getattr(
            settings,
            'DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO',
            'mailbox_attachments/%Y/%m/%d/'
        ),
        'store_original_message': getattr(
            settings,
            'DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE',
            False
        ),
        'compress_original_message': getattr(
            settings,
            'DJANGO_MAILBOX_COMPRESS_ORIGINAL_MESSAGE',
            False
        ),
        'original_message_compression': getattr(
            settings,
            'DJANGO_MAILBOX_ORIGINAL_MESSAGE_COMPRESSION',
            6
        ),
        'default_charset': getattr(
            settings,
            'DJANGO_MAILBOX_default_charset',
            'iso8859-1',
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