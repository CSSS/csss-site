from about.models import Officer, UnProcessedOfficer
from csss.views.determine_user_role import user_is_officer_in_past_5_terms, user_is_current_sys_admin, \
    user_is_current_election_officer, user_is_current_webmaster_or_doa
from csss.views.exceptions import InvalidPrivilege


def validate_request_to_update_digital_resource_permissions(request):
    """
    Ensure that the request is made by either root or someone who is allowed to modify the
     digital resources permissions

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is made by someone who is not allowed to modify the digital resources
     permissions
    """
    if request.user.username == "root":
        return
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_officer_in_past_5_terms(request, unprocessed_officers=unprocessed_officers, officers=officers):
        return
    raise InvalidPrivilege(request)


def validate_request_to_update_gdrive_permissions(request):
    """
    Ensure that the request is made by either root or someone who is allowed to modify the
     Google Drive permissions

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is made by someone who is not allowed to modify the google drive permissions
    """
    validate_request_to_update_digital_resource_permissions(request)


def validate_request_to_update_github_permissions(request):
    """
    Ensure that the request is made by either root or someone who is allowed to modify the
     GitHub permissions

    Keyword Argument
    request -- the django request object
    endpoint -- the endpoint to call if there is an error

    Exception thrown if the request is made by someone who is not allowed to modify the digital resources
    """
    if request.user.username == "root":
        return
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_sys_admin(request, unprocessed_officers=unprocessed_officers, officers=officers):
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
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_election_officer(request, unprocessed_officers=unprocessed_officers, officers=officers):
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
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all()
    if user_is_current_webmaster_or_doa(request, unprocessed_officers=unprocessed_officers, officers=officers):
        return
    raise InvalidPrivilege(request)
