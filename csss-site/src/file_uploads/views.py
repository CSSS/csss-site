# from pathlib import Path

from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.conf import settings

from . import forms


class BaseFormView(generic.FormView):
    template_name = 'file_uploads/example_form.html'

    def get_context_data(self, *args, **kwargs):
        groups = list(self.request.user.groups.values_list('name', flat=True))
        kwargs.update(
            tab='documents',
            authenticated=self.request.user.is_authenticated,
            Exec=('Exec' in groups),
            ElectionOfficer=('ElectionOfficer' in groups),
            Staff=self.request.user.is_staff,
            Username=self.request.user.username,
            URL_ROOT=settings.URL_ROOT
        )
        return super().get_context_data(*args, **kwargs)

    def get_success_url(self):
        return reverse('success')

    def form_valid(self, form):
        form.save()
        return super(BaseFormView, self).form_valid(form)


def success(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'documents',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': settings.URL_ROOT
    }
    return render(request, 'file_uploads/success.html', context)


class SubmissionUpoadSuccess(generic.TemplateView):
    template_name = 'file_uploads/example_form.html'


class SubmissionUploadPage(BaseFormView):
    form_class = forms.MultipleFileExampleForm
