import django_bootstrap3_form

from django_file_form.forms import MultipleUploadedFileField, FileFormMixin

from .models import UserSubmission, UploadedFile


class BaseForm(FileFormMixin, django_bootstrap3_form.BootstrapForm):
    title = django_bootstrap3_form.CharField()


class MultipleFileExampleForm(BaseForm):
    input_file = MultipleUploadedFileField()

    def save(self):
        example = UserSubmission.objects.create(
            title=self.cleaned_data['title']
        )
        print("[MultipleFileExampleForm] self.cleaned_data="+str(self.cleaned_data))
        for f in self.cleaned_data['input_file']:
            print("[MultipleFileExampleForm] input_file="+str(f))
            UploadedFile.objects.create(
                example=example,
                input_file=f
            )

        self.delete_temporary_files()
