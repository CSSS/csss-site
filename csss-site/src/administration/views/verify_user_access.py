from django.http import HttpResponseRedirect

from administration.Constants import CURRENT_WEBMASTER_OR_DOA, OFFICER_IN_PAST_5_TERMS, CURRENT_ELECTION_OFFICER
from csss.views_helper import create_main_context


def verify_user_can_create_officer_creation_links(request, tab):
    context = create_main_context(request, tab)
    if not (CURRENT_WEBMASTER_OR_DOA in request.session):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def verify_user_can_upload_officer_lists(request, tab):
    context = create_main_context(request, tab)
    if not (CURRENT_WEBMASTER_OR_DOA in request.session):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def verify_user_can_update_position_mappings(request, tab):
    context = create_main_context(request, tab)
    if not (CURRENT_WEBMASTER_OR_DOA in request.session):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def create_context_and_verify_user_can_update_github_mappings(request, tab):
    context = create_main_context(request, tab)
    if not (verify_user_can_update_github_mappings(request)):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def verify_user_can_update_github_mappings(request):
    return CURRENT_WEBMASTER_OR_DOA in request.session


def create_context_and_verify_user_was_an_officer_in_past_5_terms(request, tab):
    context = create_main_context(request, tab)
    if not (verify_user_was_an_officer_in_past_5_terms(request)):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def verify_user_was_an_officer_in_past_5_terms(request):
    return OFFICER_IN_PAST_5_TERMS in request.session


def create_context_and_verify_user_can_manage_elections(request, tab):
    context = create_main_context(request, tab)
    if not (verify_user_can_manage_elections(request)):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def verify_user_can_manage_elections(request):
    return CURRENT_ELECTION_OFFICER in request.session
