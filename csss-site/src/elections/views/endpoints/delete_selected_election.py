import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY
from elections.models import Election
from elections.views.Constants import ELECTION_ID_KEY, TAB_STRING
from elections.views.utils.display_error_message import display_error_message

logger = logging.getLogger('csss_site')


def delete_selected_election(request):
    logger.info(
        f"[administration/delete_selected_election.py delete_selected_election()] request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(
        request, TAB_STRING
    )
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if election_id_is_valid(request.POST):
        Election.objects.get(id=int(request.POST[ELECTION_ID_KEY])).delete()
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/')
    return display_error_message(request, context, "Could not detect the election ID in your request")


def election_id_is_valid(request_obj):
    return ELECTION_ID_KEY in request_obj and f"{request_obj[ELECTION_ID_KEY]}".isdigit() and \
           (len(Election.objects.all().filter(id=int(request_obj[ELECTION_ID_KEY]))) == 1)
