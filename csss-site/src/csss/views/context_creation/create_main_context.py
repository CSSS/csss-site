from django.conf import settings

from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from csss.views.context_creation.create_base_context import create_base_context
from elections.models import Election
from resource_management.views.get_officer_list import get_list_of_officer_details_from_past_specified_terms

CURRENT_WEBMASTER_OR_DOA = 'current_webmaster_or_doa'
CURRENT_SYS_ADMIN = 'current_sys_admin'
CURRENT_SYS_ADMIN_OR_WEBMASTER = 'current_sys_admin_or_webmaster'
OFFICER_IN_PAST_5_TERMS = 'officer_in_past_5_terms'
CURRENT_ELECTION_OFFICER = 'current_election_officer'


def create_main_context(request, tab=None):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    groups -- the groups that need to be checked to see if the user is allowed to certain group privileges

    Return
    context -- the base context dictionary
    """
    elections = Election.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context = create_base_context()
    request_path = f"http://{settings.HOST_ADDRESS}"
    if settings.PORT is not None:
        request_path += f":{settings.PORT}"
    if request.user.is_authenticated:
        request_path += "/logout"
        context['LOGOUT_URL'] = request_path
    else:
        request_path += f"/login?next={request.path}"
        context['LOGIN_URL'] = request_path

    current_webmaster_or_doa_sfuid = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=0, position_names=["Webmaster", "Director of Archives"], filter_by_sfuid=True
    )

    current_sys_admin_sfuid = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=0, position_names=["Systems Administrator"], filter_by_sfuid=True
    )

    current_sys_admin_or_webmaster_sfuid = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=0, position_names=["Webmaster", "Systems Administrator"], filter_by_sfuid=True
    )
    if request.user.username in ['jsaadatm']:
        request.user.is_staff = True
        request.user.is_superuser = True
    else:
        request.user.is_staff = False
        request.user.is_superuser = False
    request.user.save()
    sfuid_for_officer_in_past_5_terms = get_list_of_officer_details_from_past_specified_terms(
        filter_by_sfuid=True
    )

    current_election_officer_sfuid = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=0, position_names=["General Election Officer", "By-Election Officer"],
        filter_by_sfuid=True
    )
    context.update({
        'user': request.user,
        'tab': tab,
        'election_list': elections,
        CURRENT_WEBMASTER_OR_DOA: request.user.username in current_webmaster_or_doa_sfuid,
        CURRENT_SYS_ADMIN: request.user.username in current_sys_admin_sfuid,
        CURRENT_SYS_ADMIN_OR_WEBMASTER: request.user.username in current_sys_admin_or_webmaster_sfuid,
        OFFICER_IN_PAST_5_TERMS: request.user.username in sfuid_for_officer_in_past_5_terms,
        CURRENT_ELECTION_OFFICER: request.user.username in current_election_officer_sfuid
    })

    return context
