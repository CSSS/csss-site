from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

ERROR_MESSAGES_KEY = 'error_messages'
INVALID_PRIVILEGE_MESSAGES_KEY = 'invalid_privilege_error_messages'

class InvalidPrivilege(Exception):
    def __init__(self, request, error_message, tab=None, html=None, endpoint=None):
        self.render = None
        self.error_messages = None
        self.endpoint = None
        if endpoint is not None:
            self.error_messages = [error_message]
            self.endpoint = endpoint
        context = create_main_context(request, tab)
        if html is None:
            error_message = "No html page or endpoint was specified in exception"
            html = 'csss/error.html'
        context[INVALID_PRIVILEGE_MESSAGES_KEY] = [error_message]
        self.render = render(request, html, context)
