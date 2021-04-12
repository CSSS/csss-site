import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.views.Constants import ELECTION_MODIFY_KEY, UPDATE_JSON_KEY, ELECTION_ID_KEY, UPDATE_WEBFORM_KEY, \
    DELETE_ACTION_KEY, TAB_STRING
from elections.views.extractors.get_existing_election_by_id import get_existing_election_by_id
from elections.views.utils.display_error_message import display_error_message

logger = logging.getLogger('csss_site')

ELECTION_MODIFY_ACTIONS = [UPDATE_JSON_KEY, UPDATE_WEBFORM_KEY, DELETE_ACTION_KEY]


def determine_election_action(request):
    """
    Redirects the user to the page where they can edit the chosen election either via JSON or WebForm
    """
    logger.info("[elections/process_user_election_action.py determine_election_action()] "
                f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_MODIFY_KEY not in request.POST:
        return display_error_message(request, context, "Unable to determine user's action, please try again")
    if request.POST[ELECTION_MODIFY_KEY] not in ELECTION_MODIFY_ACTIONS:
        return display_error_message(request, context, "Incorrect user's action detected, please try again")
    if ELECTION_ID_KEY not in request.POST:
        return display_error_message(request, context, "Could not find election ID in request, please try again")
    if not (f"{request.POST[ELECTION_ID_KEY]}".isdigit() and
            get_existing_election_by_id(int(request.POST[ELECTION_ID_KEY])) is not None):
        return display_error_message(request, context, "Incorrect election ID detected, please try again")
    if request.POST[ELECTION_MODIFY_KEY] == UPDATE_JSON_KEY:
        request.session[ELECTION_ID_KEY] = request.POST[ELECTION_ID_KEY]
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_json")
    elif request.POST[ELECTION_MODIFY_KEY] == UPDATE_WEBFORM_KEY:
        request.session[ELECTION_ID_KEY] = request.POST[ELECTION_ID_KEY]
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_webform")
    elif request.POST[ELECTION_MODIFY_KEY] == DELETE_ACTION_KEY:
        request.session[ELECTION_ID_KEY] = request.POST[ELECTION_ID_KEY]
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/delete")
