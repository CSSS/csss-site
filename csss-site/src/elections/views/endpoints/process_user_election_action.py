import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY
from elections.models import Election
from elections.views.Constants import ELECTION_MODIFY_KEY, UPDATE_JSON_KEY, ELECTION_ID_KEY, UPDATE_WEBFORM_KEY, \
    DELETE_ACTION_KEY, TAB_STRING, ENDPOINT_MODIFY_VIA_JSON, ENDPOINT_MODIFY_VIA_WEBFORM, ENDPOINT_DELETE_ELECTION
from elections.views.utils.display_error_message import display_error_message

logger = logging.getLogger('csss_site')

ELECTION_MODIFY_ACTIONS = [UPDATE_JSON_KEY, UPDATE_WEBFORM_KEY, DELETE_ACTION_KEY]


def determine_election_action(request):
    """
    Redirects the user to the page where they can edit the chosen election either via JSON or WebForm
    """
    logger.info("[elections/process_user_election_action.py determine_election_action()] "
                f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(request,
                                                                                                        TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_MODIFY_KEY not in request.POST:
        return display_error_message(request, context, "Unable to determine user's action, please try again")
    if request.POST[ELECTION_MODIFY_KEY] not in ELECTION_MODIFY_ACTIONS:
        return display_error_message(request, context, "Incorrect user's action detected, please try again")
    if not election_id_is_valid(request.POST):
        return display_error_message(request, context, "Incorrect election ID detected, please try again")
    request.session[ELECTION_ID_KEY] = request.POST[ELECTION_ID_KEY]
    if request.POST[ELECTION_MODIFY_KEY] == UPDATE_JSON_KEY:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{ENDPOINT_MODIFY_VIA_JSON}")
    elif request.POST[ELECTION_MODIFY_KEY] == UPDATE_WEBFORM_KEY:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{ENDPOINT_MODIFY_VIA_WEBFORM}")
    elif request.POST[ELECTION_MODIFY_KEY] == DELETE_ACTION_KEY:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{ENDPOINT_DELETE_ELECTION}")


def election_id_is_valid(object_to_check):
    """
    Indicates if the election ID in the passed in object has a valid election id

    Keyword Argument
    request_post -- the object to check for the election ID

    Return
    bool -- True or False to indicate if the election ID is valid
    """
    return ELECTION_ID_KEY in object_to_check and f"{object_to_check[ELECTION_ID_KEY]}".isdigit() and \
        (Election.objects.all().filter(id=int(object_to_check[ELECTION_ID_KEY])) == 1)
