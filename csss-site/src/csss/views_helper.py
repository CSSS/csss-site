import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from administration.cas_login import interpret_sfu_cas_response
from elections.models import Election

ERROR_MESSAGE_KEY = 'error_message'
ERROR_MESSAGES_KEY = 'error_messages'

logger = logging.getLogger('csss_site')


def create_main_context(request, tab):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    groups -- the groups that need to be checked to see if the user is allowed to certain group privileges

    Return
    context -- the base context dictionary
    """
    interpret_sfu_cas_response(request)
    elections = Election.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context = _create_base_context()
    request_path = None
    if request.COOKIES.get("sfuid", None) is None:
        request_path = f"https://cas.sfu.ca/cas/login?service=http://{settings.HOST_ADDRESS}"
        if settings.PORT is not None:
            request_path += f":{settings.PORT}"
        request_path += f"{request.path}"

    context.update({
        'username': request.COOKIES.get("sfuid", False),
        'cas_login': request_path,
        'tab': tab,
        'election_list': elections,
        'current_webmaster_or_doa': request.COOKIES.get("current_webmaster_or_doa", False),
        'current_sys_admin': request.COOKIES.get("current_sys_admin", False),
        'current_sys_admin_or_webmaster': request.COOKIES.get("current_sys_admin_or_webmaster", False),
        'officer_in_past_5_terms': request.COOKIES.get("officer_in_past_5_terms", False),
        'current_election_officer': request.COOKIES.get("current_election_officer", False)
    })
    return context



def create_frosh_context():
    """
    creates the context dictionary for the frosh webpages

    Return
    context -- the frosh webpages context dictionary
    """
    return _create_base_context()


def _create_base_context():
    """
    creates the base context dictionary that contains only the URL_ROOT

    Return
    context -- the base context dictionary

    """
    context = {
        'URL_ROOT': settings.URL_ROOT,
    }
    return context


def verify_access_logged_user_and_create_context_for_elections(request, tab):
    """
    Makes sure that the user is allowed to access the election page and returns
    the context dictionary

    Keyword Argument
    request -- the django request object
    tab -- the tab that needs to be specified in the context

    Return
    HttpResponseRedirect -- either None or the redirect object that redirect to the error page
    error_message -- the error message if the user is not allowed to access the election pages
    context -- the base context dictionary
    """
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    if not (ELECTION_MANAGEMENT_GROUP_NAME in groups):
        return HttpResponseRedirect('/error'), "You are not authorized to access this page", context
    return None, None, context


def verify_access_logged_user_and_create_context(request, tab):
    """
    make sure that the user is logged in with the sufficient level of access to access the page

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified in the context

    Return
    HttpResponseRedirect -- returns a redirect to /error if the user is not allowed to access
     the page or None if they are
    error_message -- the error message if the user is not allowed to access the page
    context -- the context object to pass to html if user is allowed to access the page
    """
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    if not (request.user.is_staff or 'officer' in groups):
        return HttpResponseRedirect(
            '/error'), "You are not authorized to access this page", None
    return None, None, context


def there_are_multiple_entries(post_dict, key_to_read):
    """
    Check to see if the given dictionary has an array or a single element at the specified key

    Keyword Argument
    post_dict -- the dictionary to check
    key_to_read -- the key in the dictionary to check

    return:
    True if the key contains an erray of elements rather than just 1 element. or None if that
     key is not in the dictionary
    """
    if key_to_read not in post_dict:
        return None
    return isinstance(post_dict[key_to_read], list)


