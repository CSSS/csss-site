from urllib.error import HTTPError
from xml.etree.ElementTree import ParseError

from django.conf import settings
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django_cas_ng.views import LoginView as CasLoginView
from django_cas_ng.views import LogoutView as CASLogoutView

from csss.views.exceptions import CASAuthenticationMethod
from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_sys_admin_or_webmaster_sfuid

CAS_GROUP_NAME = 'CAS_users'


class LoginView(CasLoginView):

    def successful_login(self, request, next_page):
        login_redirect = super().successful_login(request, next_page)
        if request.user.username in get_current_sys_admin_or_webmaster_sfuid():
            request.user.is_staff = True
            request.user.is_superuser = True
            request.user.save()
        groups = Group.objects.all().filter(name=CAS_GROUP_NAME)
        if len(groups) == 1:
            groups[0].user_set.add(request.user)
        else:
            group = Group(name=CAS_GROUP_NAME)
            group.save()
            group.user_set.add(request.user)
        return login_redirect

    def get(self, request):
        # Override to catch exceptions caused by CAS server not responding, which happens and is beyond our control.
        try:
            return super().get(request)
        except IOError as e:
            # Ignore a minimal set of errors we have actually seen result from CAS outages
            if e.errno in [104, 110, 'socket error']:
                pass

            # HTTPError is a subclass of OSError, which IOError is an alias for.
            # Sometimes, the CAS server seems to just return a 500 internal server error.  Let's handle that the
            # same way as the above case.
            elif isinstance(e, HTTPError):
                if e.code == 500:
                    pass
                else:
                    # Any other HTTPError should bubble up and let us know something horrible has happened.
                    raise CASAuthenticationMethod(
                        request,
                        error_message=f"Encountered an unexpected exception of: {e}"
                    )
            else:
                raise CASAuthenticationMethod(request, error_message=f"The errno is {e.errno}: {e}.")
        except ParseError:
            pass
        raise CASAuthenticationMethod(request, error_message="Login failed because of a CAS error.")


class LogoutView(CASLogoutView):

    def get(self, request):
        groups = Group.objects.all().filter(name=CAS_GROUP_NAME)
        if len(groups) == 1 and len(groups[0].user_set.all().filter(username=request.user.username)) == 1:
            return super().get(request)
        dj_logout(request)
        return HttpResponseRedirect(settings.URL_ROOT)
