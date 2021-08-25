from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import InvalidPrivilege
from csss.views.request_validation import election_officer_request_allowed


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
            "incorrect permission for election management", context=context,
            html='csss/error.html'
        )
    if election_officer_request_allowed(request, groups):
        return context
    raise InvalidPrivilege(
        request, "You are not allowed to manage the elections.", context, html=html, endpoint=endpoint
    )
