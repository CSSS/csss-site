import logging
import datetime

from django.conf import settings
from django.http import HttpResponseRedirect

from about.models import Term
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
    True if the key contains an erray of elements rather than just 1 element. or None if that
     key is not in the dictionary
    """
    if key_to_read not in post_dict:
        return None
    return isinstance(post_dict[key_to_read], list)


def get_current_term():
    """
    Get the term number for the current term

    Return
    the term_number that fits the convention YYY<1/2/3>
    """
    current_date = datetime.datetime.now()
    return get_term_number_for_specified_year_and_month(current_date.month, current_date.year)


def get_current_term_obj():
    """
    Get the term object that corresponds to current term

    Return
    term -- either the term object if it exists or None
    """
    terms = Term.objects.all().filter(term_number=get_current_term())
    return None if len(terms) == 0 else terms[0]


def get_past_x_term_obj(relevant_previous_terms=0):
    """
    Gets the past X terms that are specified

    Keyword Argument
    relevant_previous_terms - if 0 specified, only get current term
     if 1 is specified get current and previous term and so forth

     Return
     terms -- list of applicable terms if Found, otherwise None
    """
    term_active = get_current_term()
    relevant_previous_terms += 1
    relevant_terms = []
    for index in range(0, relevant_previous_terms):
        terms = Term.objects.all().filter(term_number=term_active)
        if len(terms) > 0:
            relevant_terms.append(terms[0])
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8

    return None if len(relevant_terms) == 0 else relevant_terms


def get_term_number_for_specified_year_and_month(month, year):
    """
    get the term_number for the term that maps to the specified month and year

    keyword argument
    month -- the month's number (1-12)
    year -- the year's number

    return: the term_number that fits the convention YYY<1/2/3>
    """
    term_active = (year * 10)
    if int(month) <= 4:
        term_active += 1
    elif int(month) <= 8:
        term_active += 2
    else:
        term_active += 3
    return term_active
