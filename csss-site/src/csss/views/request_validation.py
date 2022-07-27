from about.models import Officer
from csss.views.determine_user_role import user_is_officer_in_past_5_terms, user_is_current_sys_admin, \
    user_is_current_election_officer, user_is_current_webmaster_or_doa
from csss.views.exceptions import InvalidPrivilege
from resource_management.models import NaughtyOfficer


def validate_request_to_update_digital_resource_permissions(request):
    """
    Ensure that the request is made by either root or the someone who is allowed to modify the
     digital resources permissions

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is made by someone who is not allowed to modify the digital resources
     permissions
    """
    if request.user.username == "root":
        return
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_officer_in_past_5_terms(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request)


def validate_request_to_update_gdrive_permissions(request):
    """
    Ensure that the request is made by either root or the someone who is allowed to modify the
     google drive permissions

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is made by someone who is not allowed to modify the google drive permissions
    """
    validate_request_to_update_digital_resource_permissions(request)


def validate_request_to_update_github_permissions(request):
    """
    Ensure that the request is made by either root or the someone who is allowed to modify the
     github permissions

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is made by someone who is not allowed to modify the digital resources
    """
    if request.user.username == "root":
        return
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_sys_admin(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request)


def validate_request_to_delete_election(request):
    """
    Ensure that the request is made by either root or the election officer

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is not made by either root or the election officer
    """
    if request.user.username == "root":
        return
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_election_officer(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request)


def validate_request_to_delete_new_officer(request):
    """
    Ensure that the request is made by either root or DoA or Webmaster

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is not made by either root or DoA or Webmaster
    """
    if request.user.username == "root":
        return
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_webmaster_or_doa(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request)
