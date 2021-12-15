from csss.views.views import ERROR_MESSAGES_KEY


def create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=None):
    """
    Adds the error message to the context dictionary

    Keyword Arguments
    context -- the context dictionary that has to be populated for the html_snippet_for_general_error_validations.html
    error_messages -- error message to display
    """
    context[ERROR_MESSAGES_KEY] = error_messages



