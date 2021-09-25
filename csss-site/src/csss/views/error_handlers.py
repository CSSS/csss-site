from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import InvalidPrivilege, NoAuthenticationMethod
from csss.views.views import ERROR_MESSAGES_KEY


class HandleBusinessExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, InvalidPrivilege):
            return exception.render
        if isinstance(exception, NoAuthenticationMethod):
            return exception.render
        context = create_main_context(request, 'index')
        context[ERROR_MESSAGES_KEY] = [f"Encountered an unexpected exception of: {exception}"]
        return render(request, 'csss/error.html', context)
