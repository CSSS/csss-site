import logging
import os
import pathlib

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
        if options['download']:
            os.system(
                "rm -fr ../../media_root || true; "
                "mkdir -p ../../media_root || true; "
                "wget -r --no-host-directories https://dev.sfucsss.org/mailbox_attachments/ -R '*html*' "
                "-P ../../media_root/ || true"
            )
        else:
            [
                self.create_attachments(message) for message in Message.objects.all().order_by('-id')
            ]

    @staticmethod
    def create_attachments(message):

        attachments_to_create = [attachment.document for attachment in message.attachments.all()]

        for attachment_to_create in attachments_to_create:
            try:
                file_path = attachment_to_create.path
                file_path = file_path[:file_path.rfind("/"):]
                pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
                open(attachment_to_create.path, 'w').close()
            except Exception:
                pass
