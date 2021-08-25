from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import InvalidPrivilege
from csss.views.request_validation import officer_request_allowed


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
            "incorrect permission for officer access", context=context,
            html='csss/error.html'
        )
    if officer_request_allowed(request, groups=groups):
        return context
    if context_function is not None:
        context = context_function(context)
    raise InvalidPrivilege(request, "You are not allowed to access this page", context, html=html, endpoint=endpoint)
