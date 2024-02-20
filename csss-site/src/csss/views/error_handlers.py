from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
import traceback

from csss.setup_logger import Loggers
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import InvalidPrivilege, NoAuthenticationMethod, CASAuthenticationMethod, \
    UnProcessedNotDetected
from csss.views.views import ERROR_MESSAGES_KEY


class HandleBusinessExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger = Loggers.get_logger()
        if isinstance(exception, InvalidPrivilege):
            if request.user.is_authenticated:
                return exception.render
            else:
                base_url = f"http://{settings.HOST_ADDRESS}"
                # this is necessary if the user is testing the site locally and therefore
                # is using the port to access the browser
                if settings.PORT is not None:
                    base_url += f":{settings.PORT}"
                return HttpResponseRedirect(f"{base_url}/login?next={request.path}")
        if isinstance(exception, NoAuthenticationMethod):
            return exception.render
        if isinstance(exception, CASAuthenticationMethod):
            return exception.render
        if isinstance(exception, UnProcessedNotDetected):
            return exception.render
        context = create_main_context(request, 'index')
        logger.exception(traceback.format_exc())
        context[ERROR_MESSAGES_KEY] = [f"Encountered an unexpected exception of: {exception}"]
        return render(request, 'csss/error_htmls/unknown_error.html', context)
