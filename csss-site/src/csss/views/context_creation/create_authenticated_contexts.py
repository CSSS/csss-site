from about.models import Officer
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.determine_user_role import user_is_current_webmaster_or_doa, user_is_current_sys_admin, \
    user_is_officer_in_past_5_terms, user_is_current_election_officer
from csss.views.exceptions import InvalidPrivilege
from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_webmaster_or_doa_sfuid, get_current_sys_admin_sfuid, \
    get_sfuid_for_officer_in_past_5_terms, get_current_election_officer_sfuid
from resource_management.models import NaughtyOfficer


def create_context_for_officer_creation_links(request, tab=None, endpoint=None, html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_webmaster_or_doa, tab=tab, endpoint=endpoint,
        html=html, naughty_officers=naughty_officers, officers=officers
    )


def create_context_for_uploading_and_download_officer_lists(request, tab=None, endpoint=None, html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_webmaster_or_doa, tab=tab, endpoint=endpoint,
        html=html, naughty_officers=naughty_officers, officers=officers
    )


def create_context_for_updating_position_mappings(request, tab=None, endpoint=None, html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_webmaster_or_doa, tab=tab, endpoint=endpoint,
        html=html, naughty_officers=naughty_officers, officers=officers
    )


def create_context_for_updating_github_mappings_and_permissions(request, tab=None, endpoint=None,
                                                                html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_sys_admin, tab=tab, endpoint=endpoint,
        html=html, naughty_officers=naughty_officers, officers=officers
    )


def create_context_for_current_and_past_officers_details(request, tab=None, endpoint=None, html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_officer_in_past_5_terms, tab=tab, endpoint=endpoint,
        html=html, naughty_officers=naughty_officers, officers=officers
    )


def create_context_for_google_drive_permissions(request, tab=None, endpoint=None, html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_officer_in_past_5_terms, tab=tab, endpoint=endpoint,
        html=html, naughty_officers=naughty_officers, officers=officers
    )


def create_context_for_election_officer(request, tab=None, endpoint=None, html=None):
    naughty_officers = NaughtyOfficer.objects.all()
    officers = Officer.objects.all()
    return _create_context_for_authenticated_user(
        request, authentication_method=user_is_current_election_officer, tab=tab, endpoint=endpoint, html=html,
        naughty_officers=naughty_officers, officers=officers
    )


def _create_context_for_authenticated_user(request, authentication_method=None,
                                           tab=None, endpoint=None, html=None, naughty_officers=None, officers=None):
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
    if authentication_method(request, naughty_officers=naughty_officers, officers=officers):
        return create_main_context(
            request, tab,
            current_election_officer_sfuid=get_current_election_officer_sfuid(naughty_officers=naughty_officers,
                                                                              officers=officers),
            sfuid_for_officer_in_past_5_terms=get_sfuid_for_officer_in_past_5_terms(naughty_officers=naughty_officers,
                                                                                    officers=officers),
            current_sys_admin_sfuid=get_current_sys_admin_sfuid(naughty_officers=naughty_officers, officers=officers),
            current_webmaster_or_doa_sfuid=get_current_webmaster_or_doa_sfuid(naughty_officers=naughty_officers,
                                                                              officers=officers)
        )
    if endpoint is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", endpoint=endpoint)
    if html is not None:
        raise InvalidPrivilege(request, "You are not allowed to access this page", html=html)
