import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.views.views import ERROR_MESSAGES_KEY
from csss.views.request_validation import validate_request_to_delete_election
from elections.models import Election
from elections.views.Constants import ELECTION_ID
from elections.views.validators.validate_election_id import validate_election_id_in_dict

logger = logging.getLogger('csss_site')


def delete_selected_election(request):
    logger.info("[administration/delete_selected_election.py delete_selected_election()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    endpoint = f'{settings.URL_ROOT}elections/'
    validate_request_to_delete_election(request, endpoint=endpoint)
    success, error_message = validate_election_id_in_dict(request.POST)
    if success:
        Election.objects.get(id=int(request.POST[ELECTION_ID])).delete()
    else:
        request.session[ERROR_MESSAGES_KEY] = [error_message]
    return HttpResponseRedirect(endpoint)
