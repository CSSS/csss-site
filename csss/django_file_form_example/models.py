import six

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class Example(models.Model):
	fs = FileSystemStorage(location=settings.MEDIA_ROOT)

	title = models.CharField(max_length=255)
	input_file = models.FileField(max_length=255, upload_to='example', storage=fs)


class Event_Uploads(models.Model):
	title = models.CharField(max_length=255)
	submitter_name = models.CharField("Submitter Name",blank=True, max_length=500)
	submission_name = models.CharField("Submission Name", max_length=500)
	submitter_info =  models.CharField("Submission Name",blank=True, max_length=500)
	optional_info = models.TextField("Optional Information",blank=True,max_length=50)

@six.python_2_unicode_compatible
class Event_File(models.Model):
	fs = FileSystemStorage(location=settings.MEDIA_ROOT)

	example = models.ForeignKey(Event_Uploads, related_name='files', on_delete=models.CASCADE)
	input_file = models.FileField(max_length=255, upload_to='example', storage=fs)

	def __str__(self):
		return six.text_type(self.input_file)
