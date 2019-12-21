# from pathlib import Path

from django.views import generic
from django.urls import reverse

from . import forms

class BaseFormView(generic.FormView):
    template_name = 'example_form.html'

    def get_success_url(self):
        return reverse('example_success')

    def form_valid(self, form):
        form.save()
        return super(BaseFormView, self).form_valid(form)

class SubmissionUpoadSuccess(generic.TemplateView):
    template_name = 'example_form.html'


class SubmissionUploadPage(BaseFormView):
    form_class = forms.MultipleFileExampleForm
