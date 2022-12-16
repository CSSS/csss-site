import json

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.setup_logger import get_logger
from csss.views.request_validation import validate_request_to_delete_election
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election


def delete_selected_election(request, slug):
    logger = get_logger()
    logger.info("[administration/delete_selected_election.py delete_selected_election()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    validate_request_to_delete_election(request)
    if len(Election.objects.all().filter(slug=slug)) != 1:
        request.session[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
    Election.objects.get(slug=slug).delete()
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
