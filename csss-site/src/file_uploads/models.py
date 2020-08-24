import six
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class UserSubmission(models.Model):
    title = models.CharField(max_length=255)


class UploadedFile(models.Model):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)

    example = models.ForeignKey(UserSubmission, related_name='files', on_delete=models.CASCADE)
    input_file = models.FileField(
        max_length=255,
        upload_to=settings.FILE_FORM_MASTER_DIR+'multiFileUploads/',
        storage=fs
    )

    def __str__(self):
        return six.text_type(self.input_file)
