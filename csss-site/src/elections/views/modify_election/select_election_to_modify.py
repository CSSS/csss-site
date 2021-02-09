import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from elections.models import Election
from elections.views.election_management import TAB_STRING, ELECTION_MODIFY_POST_KEY, UPDATE_JSON_POST_KEY, \
    ELECTION_ID_POST_KEY, ELECTION_ID_SESSION_KEY, UPDATE_WEBFORM_POST_KEY, DELETE_ACTION_POST_KEY

logger = logging.getLogger('csss_site')


def show_page_where_user_can_select_election_to_update(request):
    """Shows the page where the user can choose an election and whether they want to update it via JSON or WebForm"""
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    elections = Election.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context.update({'elections': elections})
    return render(request, 'elections/update_election/list_elections_to_modify.html', context)


def determine_election_action(request):
    """Redirects the user to the page where they can edit the chosen election either via JSON or WebForm"""
    logger.info(f"[administration/election_management.py determine_election_action()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ELECTION_MODIFY_POST_KEY in request.POST:
        if request.POST[ELECTION_MODIFY_POST_KEY] == UPDATE_JSON_POST_KEY and ELECTION_ID_POST_KEY in request.POST:
            request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_json")
        elif request.POST[ELECTION_MODIFY_POST_KEY] == UPDATE_WEBFORM_POST_KEY and \
                ELECTION_ID_POST_KEY in request.POST:
            request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/show_update_webform")
        elif request.POST[ELECTION_MODIFY_POST_KEY] == DELETE_ACTION_POST_KEY \
                and ELECTION_ID_POST_KEY in request.POST:
            request.session[ELECTION_ID_SESSION_KEY] = request.POST[ELECTION_ID_POST_KEY]
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/delete")
    logger.info(
        "[administration/election_management.py determine_election_action()] action "
        "is not detected, returning /elections/select_election"
    )
    return HttpResponseRedirect(f"{settings.URL_ROOT}elections/select_election")
