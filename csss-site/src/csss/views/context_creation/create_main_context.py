from django.conf import settings

from about.models import Officer, UnProcessedOfficer
from csss.models import CSSSError
from csss.views.context_creation.create_base_context import create_base_context
from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_election_officer_sfuid, get_current_sys_admin_sfuid, \
    get_current_webmaster_or_doa_sfuid, get_sfuid_for_officer_in_past_5_terms, \
    get_sfuid_for_current_executive_officers
from elections.models import Election

CURRENT_WEBMASTER_OR_DOA = 'current_webmaster_or_doa'
CURRENT_SYS_ADMIN = 'current_sys_admin'
CURRENT_SYS_ADMIN_OR_WEBMASTER = 'current_sys_admin_or_webmaster'
OFFICER_IN_PAST_5_TERMS = 'officer_in_past_5_terms'
CURRENT_ELECTION_OFFICER = 'current_election_officer'
ROOT_USER = 'root_user'


def create_main_context(request, tab=None, current_election_officer_sfuid=None,
                        sfuid_for_officer_in_past_5_terms=None, current_sys_admin_sfuid=None,
                        current_webmaster_or_doa_sfuid=None, officers=None, unprocessed_officers=None):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    current_election_officer_sfuid -- the SFUID for the current election officer
    sfuid_for_officer_in_past_5_terms -- a list that contains the SFUIDs for anyone who has been an officer
     in the past 5 terms
    current_sys_admin_sfuid -- the SFUID for the current sys admin
    current_webmaster_or_doa_sfuid -- a list that contains the SFUIDs for the current webmaster or DoA
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    context -- the base context dictionary
    """

    context = create_base_context()
    if request.user.username != "root":
        if current_election_officer_sfuid is None or sfuid_for_officer_in_past_5_terms is None or \
                current_sys_admin_sfuid is None or current_webmaster_or_doa_sfuid is None:
            if unprocessed_officers is None:
                unprocessed_officers = UnProcessedOfficer.objects.all()
            if officers is None:
                officers = Officer.objects.all().order_by('-start_date')

        if current_election_officer_sfuid is None:
            current_election_officer_sfuid = get_current_election_officer_sfuid(
                unprocessed_officers=unprocessed_officers, officers=officers
            )
        context[CURRENT_ELECTION_OFFICER] = request.user.username == current_election_officer_sfuid

        if sfuid_for_officer_in_past_5_terms is None:
            sfuid_for_officer_in_past_5_terms = get_sfuid_for_officer_in_past_5_terms(
                unprocessed_officers=unprocessed_officers, officers=officers
            )
        context[OFFICER_IN_PAST_5_TERMS] = request.user.username in sfuid_for_officer_in_past_5_terms

        if current_sys_admin_sfuid is None:
            current_sys_admin_sfuid = get_current_sys_admin_sfuid(unprocessed_officers=unprocessed_officers,
                                                                  officers=officers)
        context[CURRENT_SYS_ADMIN] = request.user.username == current_sys_admin_sfuid

        if current_webmaster_or_doa_sfuid is None:
            current_webmaster_or_doa_sfuid = get_current_webmaster_or_doa_sfuid(
                unprocessed_officers=unprocessed_officers, officers=officers
            )
        context[CURRENT_WEBMASTER_OR_DOA] = request.user.username in current_webmaster_or_doa_sfuid

        current_executive_officer_sfuids = get_sfuid_for_current_executive_officers(
            unprocessed_officers=unprocessed_officers, officers=officers)
        context['current_executive_officer'] = request.user.username in current_executive_officer_sfuids

    request_path = f"http://{settings.HOST_ADDRESS}"
    relevant_errors = CSSSError.objects.all().exclude(
        message="Couldn't do oauth2 because Install python-social-auth to use oauth2 auth for gmail\n"
    )
    context['errors_exist'] = (
        (
            (CURRENT_SYS_ADMIN in context and context[CURRENT_SYS_ADMIN]) or
            request.user.username == "root")
        and len(relevant_errors) > 0
    )
    if settings.PORT is not None:
        request_path += f":{settings.PORT}"
    if request.user.is_authenticated:
        request_path += f"{settings.URL_ROOT}logout"
        context['LOGOUT_URL'] = request_path
        context['user'] = request.user
    else:
        request_path += f"{settings.URL_ROOT}login?next={request.path}"
        context['LOGIN_URL'] = request_path

    elections = Election.objects.all().order_by('-date')
    context.update({
        'tab': tab,
        'election_list': None if len(elections) == 0 else elections,
        ROOT_USER: request.user.username == "root",
    })

    return context
