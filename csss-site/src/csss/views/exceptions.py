from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

ERROR_MESSAGES_KEY = 'error_messages'


class InvalidPrivilege(Exception):
    def __init__(self, request, error_message, tab=None, html=None, endpoint=None):
        self.render = None
        self.error_messages = None
        self.endpoint = None
        if html is not None:
            context = create_main_context(request, tab)
            context[ERROR_MESSAGES_KEY] = [error_message]
            self.render = render(request, html, context)
        elif endpoint is not None:
            self.error_messages = ["Could not detect the election ID in your deletion request"]
            self.endpoint = endpoint


class InvalidElectionIdException(Exception):
    def __init__(self, request, error_message, html, context):
        context[ERROR_MESSAGES_KEY] = [error_message]
        self.render = render(request, html, context)
