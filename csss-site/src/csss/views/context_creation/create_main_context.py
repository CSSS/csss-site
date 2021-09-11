from django.conf import settings

from about.models import Officer
from csss.views.context_creation.create_base_context import create_base_context
from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_election_officer_sfuid, get_current_sys_admin_sfuid, \
    get_current_webmaster_or_doa_sfuid, get_sfuid_for_officer_in_past_5_terms
from elections.models import Election
from resource_management.models import NaughtyOfficer

CURRENT_WEBMASTER_OR_DOA = 'current_webmaster_or_doa'
CURRENT_SYS_ADMIN = 'current_sys_admin'
CURRENT_SYS_ADMIN_OR_WEBMASTER = 'current_sys_admin_or_webmaster'
OFFICER_IN_PAST_5_TERMS = 'officer_in_past_5_terms'
CURRENT_ELECTION_OFFICER = 'current_election_officer'


def create_main_context(request, tab=None, current_election_officer_sfuid=None,
                        sfuid_for_officer_in_past_5_terms=None, current_sys_admin_sfuid=None,
                        current_webmaster_or_doa_sfuid=None, officers=None, naughty_officers=None):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    groups -- the groups that need to be checked to see if the user is allowed to certain group privileges

    Return
    context -- the base context dictionary
    """

    context = create_base_context()

    if current_election_officer_sfuid is None or sfuid_for_officer_in_past_5_terms is None or \
            current_sys_admin_sfuid is None or current_webmaster_or_doa_sfuid is None:
        if naughty_officers is None:
            naughty_officers = NaughtyOfficer.objects.all()
        if officers is None:
            officers = Officer.objects.all()

    if current_election_officer_sfuid is None:
        current_election_officer_sfuid = get_current_election_officer_sfuid(naughty_officers=naughty_officers,
                                                                            officers=officers)
    if sfuid_for_officer_in_past_5_terms is None:
        sfuid_for_officer_in_past_5_terms = get_sfuid_for_officer_in_past_5_terms(naughty_officers=naughty_officers,
                                                                                  officers=officers)

    if current_sys_admin_sfuid is None:
        current_sys_admin_sfuid = get_current_sys_admin_sfuid(naughty_officers=naughty_officers,
                                                              officers=officers)
    if current_webmaster_or_doa_sfuid is None:
        current_webmaster_or_doa_sfuid = get_current_webmaster_or_doa_sfuid(naughty_officers=naughty_officers,
                                                                            officers=officers)

    request_path = f"http://{settings.HOST_ADDRESS}"
    if settings.PORT is not None:
        request_path += f":{settings.PORT}"
    if request.user.is_authenticated:
        request_path += "/logout"
        context['LOGOUT_URL'] = request_path
        context['user'] = request.user
    else:
        request_path += f"/login?next={request.path}"
        context['LOGIN_URL'] = request_path

    elections = Election.objects.all().order_by('-date')
    context.update({
        'tab': tab,
        'election_list': None if len(elections) == 0 else elections,
        CURRENT_WEBMASTER_OR_DOA: request.user.username in current_webmaster_or_doa_sfuid,
        CURRENT_SYS_ADMIN: request.user.username in current_sys_admin_sfuid,
        OFFICER_IN_PAST_5_TERMS: request.user.username in sfuid_for_officer_in_past_5_terms,
        CURRENT_ELECTION_OFFICER: request.user.username in current_election_officer_sfuid
    })

    return context
