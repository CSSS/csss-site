from about.models import Officer
from csss.views.determine_user_role import user_is_officer_in_past_5_terms, user_is_current_sys_admin, \
    user_is_current_election_officer
from csss.views.exceptions import InvalidPrivilege
from resource_management.models import NaughtyOfficer


def validate_request_to_update_digital_resource_permissions(request, endpoint=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_officer_in_past_5_terms(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)


def validate_request_to_update_gdrive_permissions(request, endpoint=None):
    validate_request_to_update_digital_resource_permissions(request, endpoint=endpoint)


def validate_request_to_update_github_permissions(request, endpoint=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_sys_admin(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)


def validate_request_to_delete_election(request, endpoint=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_election_officer(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)
