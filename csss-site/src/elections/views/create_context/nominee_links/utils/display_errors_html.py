from csss.views_helper import ERROR_MESSAGES_KEY


def create_context_for_display_errors_html(context, error_messages=None):
    if error_messages is not None:
        context[ERROR_MESSAGES_KEY] = error_messages
