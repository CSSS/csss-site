from functools import wraps

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
import urllib.request, urllib.parse, urllib.error


def requires_role(role, get_only=None, login_url=None):
    """
    Allows access if user has the given role in ANY unit
    """

    def has_this_role(req, **kwargs):
        return has_role(role, req, get_only=get_only, **kwargs)

    actual_decorator = user_passes_test(has_this_role, login_url=login_url)
    return actual_decorator


def has_role(role, request, get_only=None, **kwargs):
    """
    Return True is the given user has the specified role in ANY unit
    """
    if isinstance(role, (list, tuple)):
        allowed = list(role)
    else:
        allowed = [role]
    if get_only and request.method == 'GET':
        if isinstance(get_only, (list, tuple)):
            allowed += list(get_only)
        else:
            allowed.append(get_only)

    roles = Role.objects_fresh.filter(person__userid=request.user.username, role__in=allowed).select_related('unit')
    request.units = set(r.unit for r in roles)
    count = roles.count()
    return count > 0


# adapted from django_cas.decorators: returns 403 on failure, and passes **kwargs to test_func.
def user_passes_test(test_func, login_url=None,
                     redirect_field_name='next', force_privacy=False):
    """Replacement for django.contrib.auth.decorators.user_passes_test that
    returns 403 Forbidden if the user is already logged in.
    """

    if not login_url:
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if test_func(request, **kwargs):
                return view_func(request, *args, **kwargs)
            elif request.user.is_authenticated:
                return ForbiddenResponse(request)
            else:
                path = '%s?%s=%s' % (login_url, redirect_field_name,
                                     urlquote(request.get_full_path()))
                return HttpResponseRedirect(path)

        return wrapper

    return decorator


def ForbiddenResponse(request, errormsg=None, exception=None):
    error = mark_safe("You do not have permission to access this resource.")
    if not request.user.is_authenticated:
        login_url = settings.LOGIN_URL + '?' + urllib.parse.urlencode({'next': request.get_full_path()})
        error += mark_safe(
            ' You are <strong>not logged in</strong>, so maybe <a href="%s">logging in</a> would help.' % (login_url))
    return HttpError(request, status=403, title="Forbidden", error=error, errormsg=errormsg)


def HttpError(request, status=404, title="Not Found", error="The requested resource cannot be found.", errormsg=None,
              simple=False, exception=None):
    if simple:
        # this case is intended to produce human-readable HTML for API errors
        template = 'simple-error.html'
    else:
        template = 'error.html'
    resp = render(request, template, {'title': title, 'error': error, 'errormsg': errormsg})
    resp.status_code = status
    return resp
