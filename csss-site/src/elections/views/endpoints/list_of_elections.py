from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.views import ERROR_MESSAGES_KEY
from elections.views.Constants import TAB_STRING

logger = get_logger()


def list_of_elections(request):
    logger.info("[elections/list_of_elections.py list_of_elections()]")
    context = create_main_context(request, TAB_STRING)

    # if user tried to delete an election that doesn't exist
    error_messages = request.session.get(ERROR_MESSAGES_KEY, None)
    if error_messages is not None:
        del request.session[ERROR_MESSAGES_KEY]
        context[ERROR_MESSAGES_KEY] = error_messages

    return render(request, 'elections/list_elections.html', context)
