from django.db import DataError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import InvalidPrivilege
from csss.views.views import ERROR_MESSAGES_KEY


class HandleBusinessExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, InvalidPrivilege):
            if exception.render is not None:
                return exception.render
            if exception.endpoint is not None and exception.error_messages is not None:
                request.session[ERROR_MESSAGES_KEY] = exception.error_messages
                return HttpResponseRedirect(exception.endpoint)
        context = create_main_context(request, 'index')
        if isinstance(exception, DataError):
            context[ERROR_MESSAGES_KEY] = [exception]
        else:
            context[ERROR_MESSAGES_KEY] = [f"Encountered an unexpected exception of: {exception}"]
        return render(request, 'csss/error.html', context)
