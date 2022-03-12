from about.models import Officer
from csss.views.determine_user_role import user_is_officer_in_past_5_terms, user_is_current_sys_admin, \
    user_is_current_election_officer
from csss.views.exceptions import InvalidPrivilege


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
    naughty_officers = None
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
    naughty_officers = None
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

    Exception thrown if the request is made by either root or the election officer
    """
    if request.user.username == "root":
        return
    naughty_officers = None
    officers = Officer.objects.all()
    if user_is_current_election_officer(request, naughty_officers=naughty_officers, officers=officers):
        return
    raise InvalidPrivilege(request)
