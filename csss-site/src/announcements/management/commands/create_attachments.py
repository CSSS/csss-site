import logging
import os
import pathlib2

from django.conf import settings
from django.core.management import BaseCommand
from django_mailbox.models import Message

logger = logging.getLogger('csss_site')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--download',
            action='store_true',
            default=False,
            help="pull the latest email attachments from staging server"
        )

    def handle(self, *args, **options):
        logger.info(options)
        download_or_create_announcement_attachments(options['download'])


def download_or_create_announcement_attachments(download=False):
    if download:
        os.system(
            "rm -fr ../../media_root || true; "
            "mkdir -p ../../media_root || true; "
            f"wget -r -X '*' "
            f"--no-host-directories {settings.STAGING_SERVER}dev_csss_website_media/mailbox_attachments/ -R '*html*' "
            " --cut-dirs=1 -P ../../media_root/ || true;"
        )
    else:
        [
            _create_attachments(message) for message in Message.objects.all().order_by('-id')
        ]


def _create_attachments(message):
    attachments_to_create = [attachment.document for attachment in message.attachments.all()]
    for attachment_to_create in attachments_to_create:
        try:
            file_path = attachment_to_create.path
            file_path = file_path[:file_path.rfind("/"):]
            pathlib2.Path(file_path).mkdir(parents=True, exist_ok=True)
            open(attachment_to_create.path, 'w').close()
        except Exception:
            pass
