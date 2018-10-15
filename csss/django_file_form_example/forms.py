from django.urls import reverse

import django_bootstrap3_form

from django_file_form.forms import UploadedFileField, MultipleUploadedFileField, FileFormMixin

from .models import Example, Event_Uploads, Event_File


class BaseForm(FileFormMixin, django_bootstrap3_form.BootstrapForm):
	title = django_bootstrap3_form.CharField()
	submitter_name = django_bootstrap3_form.CharField()
	submission_name = django_bootstrap3_form.CharField()
	submitter_info = django_bootstrap3_form.CharField()
	optional_info = django_bootstrap3_form.CharField()



class ExampleForm(BaseForm):
	input_file = UploadedFileField()

	def save(self):
		Example.objects.create(
			title=self.cleaned_data['title'],
			input_file=self.cleaned_data['input_file']
		)
		self.delete_temporary_files()


class MultipleFileExampleForm(BaseForm):
	input_file = MultipleUploadedFileField()

	def save(self):
		example = Event_Uploads.objects.create(
			title=self.cleaned_data['title'],
			submitter_name=self.cleaned_data['submitter_name'],
			submission_name=self.cleaned_data['submission_name'],
			submitter_info=self.cleaned_data['submitter_info'],
			optional_info=self.cleaned_data['optional_info'],
		)

		for f in self.cleaned_data['input_file']:
			Event_File.objects.create(
				example=example,
				input_file=f
			)

		self.delete_temporary_files()


class ExistingFileForm(ExampleForm):
	def get_upload_url(self):
		return reverse('example_handle_upload')
