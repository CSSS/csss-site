import json
import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from administration.views.verify_user_access import create_context_and_verify_user_can_manage_elections
from csss.views_helper import ERROR_MESSAGE_KEY
from elections.models import Election
from elections.views.Constants import ELECTION_ID, TAB_STRING
from elections.views.validators.validate_election_id import validate_election_id_in_dict

logger = logging.getLogger('csss_site')


def delete_selected_election(request):
    logger.info("[administration/delete_selected_election.py delete_selected_election()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    (render_value, error_message, context) = create_context_and_verify_user_can_manage_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if validate_election_id_in_dict(request.POST):
        Election.objects.get(id=int(request.POST[ELECTION_ID])).delete()
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Could not detect the election ID in your request")
    return HttpResponseRedirect(f"{settings.URL_ROOT}error")
