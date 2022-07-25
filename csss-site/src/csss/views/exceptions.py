from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context
from csss.views.views import ERROR_MESSAGES_KEY


class InvalidPrivilege(Exception):
    def __init__(self, request, tab=None):
        context = create_main_context(request, tab=tab)
        context[ERROR_MESSAGES_KEY] = ["You are not allowed to access this page"]
        self.render = render(request, 'csss/error_htmls/access_not_allowed.html', context)


class UnProcessedNotDetected(Exception):
    def __init__(self, request, tab=None):
        context = create_main_context(request, tab=tab)
        context[ERROR_MESSAGES_KEY] = [f"Could not find an unprocessed officer slot for {request.user.username}"]
        self.render = render(request, 'csss/error_htmls/access_not_allowed.html', context)


class NoAuthenticationMethod(Exception):
    def __init__(self, request, tab=None):
        context = create_main_context(request, tab=tab)
        context[ERROR_MESSAGES_KEY] = ["No Authentication Method found"]
        self.render = render(request, 'csss/error_htmls/no_authentication_method.html', context)


class CASAuthenticationMethod(Exception):
    def __init__(self, request, tab=None, error_message=None):
        context = create_main_context(request, tab=tab)
        if error_message is None:
            context[ERROR_MESSAGES_KEY] = ["Authentication method detected"]
        else:
            context[ERROR_MESSAGES_KEY] = [error_message]
        self.render = render(request, 'csss/error_htmls/login_errors.html', context)
