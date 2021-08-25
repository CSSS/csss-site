from django.http import HttpResponseRedirect

from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from csss.views.views import create_main_context


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
