import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.election_management import TAB_STRING, ELECTION_MODIFY_POST_KEY, UPDATE_JSON_POST_KEY, \
    ELECTION_ID_POST_KEY, ELECTION_ID_SESSION_KEY, UPDATE_WEBFORM_POST_KEY, DELETE_ACTION_POST_KEY
from elections.views.election_management_helper import _get_existing_election_by_id

logger = logging.getLogger('csss_site')

ELECTION_MODIFY_ACTIONS = [UPDATE_JSON_POST_KEY, UPDATE_WEBFORM_POST_KEY, DELETE_ACTION_POST_KEY]


def show_page_where_user_can_select_election_to_update(request):
    """
    Shows the page where the user can choose an election and whether they want to update it via JSON or WebForm
    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    context.update(_get_list_of_elections())
    return render(request, 'elections/update_election/list_elections_to_modify.html', context)


def determine_election_action(request):
    """
    Redirects the user to the page where they can edit the chosen election either via JSON or WebForm
    """
    logger.info(f"[administration/election_management.py determine_election_action()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_MODIFY_POST_KEY not in request.POST:
        return _display_error_message(request, context, "Unable to determine user's action, please try again")
    if request.POST[ELECTION_MODIFY_POST_KEY] not in ELECTION_MODIFY_ACTIONS:
        return _display_error_message(request, context, "Incorrect user's action detected, please try again")
    if ELECTION_ID_POST_KEY not in request.POST:
        return _display_error_message(request, context, "Could not find election ID in request, please try again")
    if not (f"{request.POST[ELECTION_ID_POST_KEY]}".isdigit() and
            _get_existing_election_by_id(int(request.POST[ELECTION_ID_POST_KEY])) is not None):
        return _display_error_message(request, context, "Incorrect election ID detected, please try again")
    if request.POST[ELECTION_MODIFY_POST_KEY] == UPDATE_JSON_POST_KEY:
        request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/election_modification_json")
    elif request.POST[ELECTION_MODIFY_POST_KEY] == UPDATE_WEBFORM_POST_KEY:
        request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_webform")
    elif request.POST[ELECTION_MODIFY_POST_KEY] == DELETE_ACTION_POST_KEY:
        request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/delete")


def _display_error_message(request, context, error_message):
    """
    Display the specified error message on the page that also lists the election that can be modified

    Keyword Argument
    request -- the django request object
    context -- the context dictionary
    error_message -- the error message that needs to be inserted into the context dictionary

    Return
    render -- directs user to the webpage that lists the election that can be modified, along with error message
    """
    context[ERROR_MESSAGES_KEY] = [error_message]
    logger.info(
        f"[administration/election_management.py determine_election_action()] {error_message} "
        f", POST={request.POST}"
    )
    context.update(_get_list_of_elections())
    return render(request, 'elections/update_election/list_elections_to_modify.html', context)


def _get_list_of_elections():
    """
    Gets the elections that need to be displayed that can be modifed by the user

    Return
    dictionary where the key is 'elections' and the value is the list of elections, or None
    """
    elections = Election.objects.all().order_by('-date')
    return {'elections': None} if len(elections) == 0 else {'elections': elections}
