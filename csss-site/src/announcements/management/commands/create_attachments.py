import pathlib

from django.core.management import BaseCommand
from django_mailbox.models import Message


class Command(BaseCommand):

    def handle(self, *args, **options):
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
            except Exception as exc:
                pass

