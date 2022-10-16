import json

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.setup_logger import get_logger
from csss.views.request_validation import validate_request_to_delete_election
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election, NomineeLink
from elections.views.Constants import DELETE_NOMINEE_LINKS_REDIRECT_PATH_KEY

logger = get_logger()


def delete_selected_election__nominee_links(request, slug):
    logger.info("[administration/delete_selected_election_nominee_links.py "
                "delete_selected_election__nominee_links()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    validate_request_to_delete_election(request)
    if len(Election.objects.all().filter(slug=slug)) != 1:
        request.session[ERROR_MESSAGES_KEY] = [f"Received invalid Election slug of {slug}"]
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
    NomineeLink.objects.all().filter(election__slug=slug).delete()
    redirect_path = request.GET.get(DELETE_NOMINEE_LINKS_REDIRECT_PATH_KEY, None)
    if redirect_path is None:
        request.session[ERROR_MESSAGES_KEY] = ["No redirect path detected"]
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
    return HttpResponseRedirect(redirect_path)
