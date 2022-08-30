from django.conf import settings
from django.http import HttpResponseRedirect

from about.models import UnProcessedOfficer
from csss.views.request_validation import validate_request_to_delete_new_officer


def delete_new_officers(request):
    validate_request_to_delete_new_officer(request)
    UnProcessedOfficer.objects.all().delete()
    return HttpResponseRedirect(f'{settings.URL_ROOT}about/specify_new_officers')
