from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from csss.views.exceptions import InvalidPrivilege


def validate_officer_request(request, endpoint=None, html=None, tab=None):
    groups = list(request.user.groups.values_list('name', flat=True))
    if html is None and endpoint is None:
        raise InvalidPrivilege(
            request,
            "No endpoint or html page was specified for redirection in case of "
            "incorrect permission for officer access", tab=tab,
            html='csss/error.html'
        )
    if officer_request_allowed(request, groups=groups):
        return
    if endpoint is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", tab=tab, endpoint=endpoint)
    if html is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", tab=tab, html=html)


def officer_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'officer' in groups


def webmaster_or_doa_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'doa' in groups or 'webmaster' in groups

def sys_admin_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'sys-admin' in groups

def webmaster_or_sys_admin_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'sys-admin' in groups or 'webmaster' in groups

def election_officer_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return ELECTION_MANAGEMENT_GROUP_NAME in groups


def validate_request_to_delete_election(request, endpoint=None):
    groups = list(request.user.groups.values_list('name', flat=True))
    if _election_officer_request_allowed(request, groups=groups):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)


def validate_request_to_manage_elections(request, endpoint=None, html=None):
    groups = list(request.user.groups.values_list('name', flat=True))
    if html is None and endpoint is None:
        raise InvalidPrivilege(
            request,
            "No endpoint or html page was specified for redirection in case of "
            "incorrect permission for officer access", tab=tab,
            html='csss/error.html'
        )
    if _election_officer_request_allowed(request, groups=groups):
        return
    if endpoint is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)
    if html is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", html=html)


def _election_officer_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return ELECTION_MANAGEMENT_GROUP_NAME in groups
