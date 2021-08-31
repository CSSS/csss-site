from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import InvalidPrivilege
from csss.views.request_validation import webmaster_or_doa_request_allowed, sys_admin_request_allowed, \
    webmaster_or_sys_admin_request_allowed, officer_request_allowed, election_officer_request_allowed


def _create_context_for_authenticated_user(request, authentication_method=None,
                                           tab=None, groups=None, endpoint=None, html=None):

    if html is None and endpoint is None:
        raise InvalidPrivilege(
            request,
            "No endpoint or html page was specified for redirection in case of "
            "incorrect permission for officer access", tab=tab,
            html='csss/error.html'
        )
    if authentication_method is None:
        if html is not None:
            raise InvalidPrivilege(
                request,
                "No authentication method detected", tab=tab,
                html=html
            )
        if endpoint is not None:
            raise InvalidPrivilege(
                request,
                "No authentication method detected", tab=tab,
                endpoint=endpoint
            )
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    if authentication_method(request, groups=groups):
        return create_main_context(request, tab=tab, groups=groups)
    if endpoint is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)
    if html is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", html=html)


def create_context_for_officer_creation_links(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=webmaster_or_doa_request_allowed, tab=tab, groups=groups, endpoint=endpoint,
        html=html
    )


def create_context_for_uploading_and_download_officer_lists(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=webmaster_or_doa_request_allowed, tab=tab, groups=groups, endpoint=endpoint,
        html=html
    )


def create_context_for_updating_position_mappings(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=webmaster_or_doa_request_allowed, tab=tab, groups=groups, endpoint=endpoint,
        html=html
    )


def create_context_for_updating_github_mappings_and_permissions(request, tab=None, groups=None, endpoint=None,
                                                                html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=sys_admin_request_allowed, tab=tab, groups=groups, endpoint=endpoint,
        html=html
    )


def create_context_for_accessing_admin(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=webmaster_or_sys_admin_request_allowed, tab=tab, groups=groups,
        endpoint=endpoint,
        html=html
    )


def create_context_for_current_and_past_officers_details(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=officer_request_allowed, tab=tab, groups=groups, endpoint=endpoint,
        html=html
    )


def create_context_for_google_drive_permissions(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=officer_request_allowed, tab=tab, groups=groups, endpoint=endpoint,
        html=html
    )


def create_context_for_election_officer(request, tab=None, groups=None, endpoint=None, html=None):
    return _create_context_for_authenticated_user(
        request, authentication_method=election_officer_request_allowed, tab=tab, groups=groups,
        endpoint=endpoint, html=html
    )


