from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

INVALID_PRIVILEGE_MESSAGES_KEY = 'invalid_privilege_error_messages'


class InvalidPrivilege(Exception):
    def __init__(self, request, tab=None):
        context = create_main_context(request, tab)
        context[INVALID_PRIVILEGE_MESSAGES_KEY] = ["You are not allowed to access this page"]
        self.render = render(request, 'csss/error.html', context)


class NoAuthenticationMethod(Exception):
    def __init__(self, request, tab=None):
        context = create_main_context(request, tab)
        context[INVALID_PRIVILEGE_MESSAGES_KEY] = ["No Authentication Method found"]
        self.render = render(request, 'csss/error.html', context)
