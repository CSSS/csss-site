import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.models import Election
from elections.views.Constants import ELECTION_ID_KEY, TAB_STRING
from elections.views.utils.display_error_message import display_error_message

logger = logging.getLogger('csss_site')


def delete_selected_election(request):
    logger.info(f"[administration/election_management.py "
                f"delete_selected_election()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_ID_KEY in request.session:
        election_id = request.session[ELECTION_ID_KEY]
        del request.session[ELECTION_ID_KEY]
        Election.objects.get(id=election_id).delete()
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/show_options_for_election_updating/')
    return display_error_message(request, context, "Could not detect the election ID in your request")
