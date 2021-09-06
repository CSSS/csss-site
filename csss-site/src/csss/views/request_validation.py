from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from csss.views.exceptions import InvalidPrivilege


def officer_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'officer' in groups


def validate_request_to_update_digital_resource_permissions(request, endpoint=None):
    groups = list(request.user.groups.values_list('name', flat=True))
    if officer_request_allowed(request, groups=groups):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)


def validate_request_to_update_gdrive_permissions(request, endpoint=None):
    validate_request_to_update_digital_resource_permissions(request, endpoint=endpoint)


def webmaster_or_doa_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'doa' in groups or 'webmaster' in groups


def sys_admin_request_allowed(request, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    return 'sys-admin' in groups


def validate_request_to_update_github_permissions(request, endpoint=None):
    groups = list(request.user.groups.values_list('name', flat=True))
    if sys_admin_request_allowed(request, groups=groups):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)


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
    if election_officer_request_allowed(request, groups=groups):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)