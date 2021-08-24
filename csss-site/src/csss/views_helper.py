import datetime
import logging

from django.conf import settings

from about.models import Term
from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from csss.views.exceptions import InvalidPrivilege
from csss.views.request_validation import officer_request_allowed, election_officer_request_allowed
from elections.models import Election

ERROR_MESSAGE_KEY = 'error_message'

logger = logging.getLogger('csss_site')


def create_main_context(request, tab=None, groups=None):
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
    elections = Election.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context = _create_base_context()
    if tab is not None:
        context['tab'] = tab
    context.update({
        'authenticated': request.user.is_authenticated,
        'authenticated_officer': ('officer' in groups),
        ELECTION_MANAGEMENT_GROUP_NAME: (ELECTION_MANAGEMENT_GROUP_NAME in groups),
        'staff': request.user.is_staff,
        'username': request.user.username,
        'election_list': elections
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


def create_context_for_election_officer(request, tab, html=None, endpoint=None):
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
    if html is None and endpoint is None:
        raise InvalidPrivilege(
            request,
            "No endpoint or html page was specified for redirection in case of "
            "incorrect permission for election management", context, html='csss/error.html'
        )
    if election_officer_request_allowed(request, groups):
        return context
    raise InvalidPrivilege(
        request, "You are not allowed to manage the elections.", context, html=html, endpoint=endpoint
    )


def create_context_for_officers(request, tab, html=None, endpoint=None, context_function=None):
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
    if html is None and endpoint is None:
        raise InvalidPrivilege(
            request,
            "No endpoint or html page was specified for redirection in case of "
            "incorrect permission for officer access", context, html='csss/error.html'
        )
    if officer_request_allowed(request, groups=groups):
        return context
    if context_function is not None:
        context = context_function(context)
    raise InvalidPrivilege(request, "You are not allowed to access this page", context, html=html, endpoint=endpoint)


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
    the term_number that fits the convention YYYY<1/2/3>
    """
    current_date = datetime.datetime.now()
    return get_term_number_for_specified_year_and_month(current_date.month, current_date.year)


def get_previous_term():
    current_date = datetime.datetime.now()
    return get_term_number_for_specified_year_and_month(current_date.month - 4, current_date.year)


def get_current_term_obj():
    """
    Get the term object that corresponds to current term

    Return
    term -- either the term object if it exists or None
    """
    terms = Term.objects.all().filter(term_number=get_current_term())
    return None if len(terms) == 0 else terms[0]


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


def get_datetime_for_beginning_of_current_term():
    """
    Gets the datetime for the beginning of the current term

    Return the datetime for the beginning of the current time where the month is Jan, May, Sept and the day is 1
    """
    current_date = datetime.datetime.now()
    while not date_is_first_day_of_term(current_date):
        current_date = current_date - datetime.timedelta(days=1)
    return current_date


def date_is_first_day_of_term(current_date):
    """
    Returns a bool to indicate if given date is the first date of a School Term

    Keyword Argument
    current_date -- the date to check

    Return
    bool
    """
    return (current_date.month == 1 or current_date.month == 5 or current_date.month == 9) and current_date.day == 1
