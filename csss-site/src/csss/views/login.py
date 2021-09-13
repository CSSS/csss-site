from urllib.error import HTTPError
from xml.etree.ElementTree import ParseError

from django.contrib.auth import logout as dj_logout
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django_cas_ng.views import LoginView as CasLoginView
from django_cas_ng.views import LogoutView as CASLogoutView

from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_sys_admin_or_webmaster_sfuid


class LoginView(CasLoginView):
    def successful_login(self, request, next_page):
        # create a LogEntry when users log in
        login_redirect = super().successful_login(request, next_page)
        if request.user.username in get_current_sys_admin_or_webmaster_sfuid():
            request.user.is_staff = True
            request.user.is_superuser = True
            request.user.save()
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
                    raise HTTPError("Got an HTTP Error when authenticating. The error is: {0!s}.".format(e))

            else:
                raise IOError("The errno is %r: %s." % (e.errno, str(e)))

        except ParseError:
            pass

        error = "<h1>Forbidden</h1><p>Login failed because of a CAS error.</p>"
        return HttpResponseForbidden(error)


class LogoutView(CASLogoutView):

    def get(self, request):
        try:
            request.user.is_staff = False
            request.user.is_superuser = False
            request.user.save()
            return super().get(request)
        except Exception as e:
            print(e)
            dj_logout(request)
            return HttpResponseRedirect("/")