# from pathlib import Path

from django.shortcuts import render
from django.views import generic
from django.urls import reverse

from administration.views.views_helper import create_context
from . import forms


class BaseFormView(generic.FormView):
    template_name = 'file_uploads/example_form.html'

    def get_success_url(self):
        return reverse('success')

    def form_valid(self, form):
        form.save()
        return super(BaseFormView, self).form_valid(form)


def success(request):
    return render(request, 'file_uploads/success.html', create_context(request, 'documents'))


class SubmissionUpoadSuccess(generic.TemplateView):
    template_name = 'file_uploads/example_form.html'


class SubmissionUploadPage(BaseFormView):
    form_class = forms.MultipleFileExampleForm
