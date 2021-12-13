from csss.views.views import ERROR_MESSAGES_KEY


def create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=None):
    context[ERROR_MESSAGES_KEY] = error_messages



