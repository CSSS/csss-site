# from pathlib import Path

from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from csss.views_helper import create_main_context
from . import forms


class BaseFormView(generic.FormView):
    template_name = 'file_uploads/example_form.html'

    def get_context_data(self, *args, **kwargs):
        kwargs.update(create_main_context(self.request, 'documents'))
        return super().get_context_data(*args, **kwargs)

    def get_success_url(self):
        return reverse('success')

    def form_valid(self, form):
        form.save()
        return super(BaseFormView, self).form_valid(form)


def success(request):
    return render(request, 'file_uploads/success.html', create_main_context(request, 'documents'))


class SubmissionUpoadSuccess(generic.TemplateView):
    template_name = 'file_uploads/example_form.html'


class SubmissionUploadPage(BaseFormView):
    form_class = forms.MultipleFileExampleForm
