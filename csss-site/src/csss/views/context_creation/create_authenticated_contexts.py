from about.models import Officer, UnProcessedOfficer
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.determine_user_role import user_is_current_webmaster_or_doa, user_is_current_sys_admin, \
    user_is_officer_in_past_5_terms, user_is_current_election_officer
from csss.views.exceptions import InvalidPrivilege, NoAuthenticationMethod, UnProcessedNotDetected
from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_webmaster_or_doa_sfuid, get_current_sys_admin_sfuid, \
    get_sfuid_for_officer_in_past_5_terms, get_current_election_officer_sfuid


def create_context_for_officer_creation_links(request, tab=None):
    """
    Create the context for the pages where officer creation links are created

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    unprocessed_officers = None
    officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_webmaster_or_doa, tab=tab,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def create_context_for_processing_unprocessed_officer(request, tab=None):
    if request.user.username == "root":
        raise UnProcessedNotDetected(request, tab=tab)
    new_officer = UnProcessedOfficer.objects.all().filter(sfu_computing_id=request.user.username).first()
    if new_officer is None:
        raise UnProcessedNotDetected(request, tab=tab)
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all().order_by('-start_date')
    return create_main_context(
        request, tab,
        current_election_officer_sfuid=get_current_election_officer_sfuid(unprocessed_officers=unprocessed_officers,
                                                                          officers=officers),
        sfuid_for_officer_in_past_5_terms=get_sfuid_for_officer_in_past_5_terms(
            unprocessed_officers=unprocessed_officers,
            officers=officers),
        current_sys_admin_sfuid=get_current_sys_admin_sfuid(unprocessed_officers=unprocessed_officers,
                                                            officers=officers),
        current_webmaster_or_doa_sfuid=get_current_webmaster_or_doa_sfuid(unprocessed_officers=unprocessed_officers,
                                                                          officers=officers)
    )


def create_context_for_uploading_and_download_officer_lists(request, tab=None):
    """
    Create the context for the pages where officer information is uploaded or downloaded

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_webmaster_or_doa, tab=tab,
        unprocessed_officers=unprocessed_officers,
        officers=officers
    )


def create_context_for_updating_position_mappings(request, tab=None):
    """
    Create the context for the pages where the officer position and email mappings are set

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_webmaster_or_doa, tab=tab,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def create_context_for_updating_github_mappings_and_permissions(request, tab=None):
    """
    Create the context for the pages where github mappings and permissions are set

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_sys_admin, tab=tab,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def create_context_for_current_and_past_officers_details(request, tab=None):
    """
    Create the context for the pages where the current or past officer details are displayed

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_officer_in_past_5_terms, tab=tab,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def create_context_for_google_drive_permissions(request, tab=None):
    """
    Create the context for the pages where the google drive permissions are managed

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_officer_in_past_5_terms, tab=tab,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def create_context_for_election_officer(request, tab=None):
    """
    Create the context for the pages where only the election officer is allowed to access

    Keyword Arguments
    request -- the django request object
    tab -- the tab for the page that the user is on
    endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_election_officer, tab=tab,
        unprocessed_officers=unprocessed_officers,
        officers=officers
    )


def create_context_for_officer_email_mappings(request, tab=None):
    officers = None
    unprocessed_officers = None
    if request.user.username != "root":
        unprocessed_officers = UnProcessedOfficer.objects.all()
        officers = Officer.objects.all().order_by('-start_date')
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_sys_admin, tab=tab,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def _create_context_for_authenticated_user(request, authentication_method=None, tab=None, unprocessed_officers=None,
                                           officers=None):
    """
    Makes sure that the context is only read for user who pass the authentication and method and that either the
    endpoint or html is specified

    Keyword Arguments
    request -- the django request object
    authentication_method -- the function to use to validate the requested access
    tab -- the tab for the page that the user is on
        endpoint -- the endpoint to redirect to if an error is experienced
    html -- the html page to redirect to if an error is experienced
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    context -- the context dictionary for the html

    Exception
    throws  InvalidPrivilege if either the html or endpoint is not specified of authentication_method is not specified
     or the user is trying to access a page they are not allowed to
    """
    if authentication_method is None:
        raise NoAuthenticationMethod(
            request, tab=tab
        )
    if not authentication_method(request, unprocessed_officers=unprocessed_officers,
                                 officers=officers):
        raise InvalidPrivilege(request, tab=tab)

    return create_main_context(
        request, tab,
        current_election_officer_sfuid=get_current_election_officer_sfuid(officers=officers,
                                                                          unprocessed_officers=unprocessed_officers),
        sfuid_for_officer_in_past_5_terms=get_sfuid_for_officer_in_past_5_terms(officers=officers,
                                                                                unprocessed_officers=unprocessed_officers),
        current_sys_admin_sfuid=get_current_sys_admin_sfuid(officers=officers,
                                                            unprocessed_officers=unprocessed_officers),
        current_webmaster_or_doa_sfuid=get_current_webmaster_or_doa_sfuid(officers=officers,
                                                                          unprocessed_officers=unprocessed_officers)
    )
