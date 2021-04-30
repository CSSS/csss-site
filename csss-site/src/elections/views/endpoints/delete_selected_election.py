import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY
from elections.models import Election
from elections.views.Constants import ELECTION_ID, TAB_STRING
from elections.views.validators.validate_election_id import validate_election_id

logger = logging.getLogger('csss_site')


def delete_selected_election(request):
    logger.info(
        f"[administration/delete_selected_election.py delete_selected_election()] request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if validate_election_id(request.POST):
        Election.objects.get(id=int(request.POST[ELECTION_ID])).delete()
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format("Could not detect the election ID in your request")
    return HttpResponseRedirect(f"{settings.URL_ROOT}error")
