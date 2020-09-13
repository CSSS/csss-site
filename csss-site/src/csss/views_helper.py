import logging
import datetime

from django.conf import settings
from django.http import HttpResponseRedirect

from elections.models import NominationPage

ERROR_MESSAGE_KEY = 'error_message'
ERROR_MESSAGES_KEY = 'error_messages'

logger = logging.getLogger('csss_site')


def create_main_context(request, tab, groups=None):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    groups -- the groups that need to be checked to see if the user is allowed to certain group privileges

    Return
    context -- the base context dictionary
    """
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    nom_pages = NominationPage.objects.all().order_by('-date')
    if len(nom_pages) == 0:
        nom_pages = None
    context = _create_base_context()
    context.update({
        'authenticated': request.user.is_authenticated,
        'authenticated_officer': ('officer' in groups),
        'election_officer': ('election_officer' in groups),
        'staff': request.user.is_staff,
        'username': request.user.username,
        'tab': tab,
        'nom_pages': nom_pages
    })
    return context


def create_frosh_context():
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
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    if not ('election_officer' in groups or request.user.is_staff):
        return HttpResponseRedirect(
            '/error'), "You are not authorized to access this page", None
    return None, None, context


def verify_access_logged_user_and_create_context(request, tab):
    """
    make sure that the user is logged in witth the sufficient level of access to access the page

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified in the context

    Return
    http redirect -- returns a redirect to /error if the user is not allowed to access the page or None if they are
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
    True if the key contains an erray of elements rather than just 1 element
    """
    return len(post_dict[key_to_read][0]) > 1


def get_current_active_term():
    """
    get the term_number for the current term

    return: the term_number that fits the convention YYY<1/2/3>
    """
    now = datetime.datetime.now()
    if int(now.month) <= 4:
        return (now.year * 10) + 1
    elif int(now.month) <= 8:
        return (now.year * 10) + 2
    else:
        return (now.year * 10) + 3
