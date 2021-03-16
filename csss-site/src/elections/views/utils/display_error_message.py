import logging

from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.utils.get_list_of_elections import get_list_of_elections

logger = logging.getLogger('csss_site')


def display_error_message(request, context, error_message):
    """
    Display the specified error message on the page that also lists the election that can be modified

    Keyword Argument
    request -- the django request object
    context -- the context dictionary
    error_message -- the error message that needs to be inserted into the context dictionary

    Return
    render -- directs user to the webpage that lists the election that can be modified, along with error message
    """
    context[ERROR_MESSAGES_KEY] = [error_message]
    logger.info(
        f"[administration/election_management.py determine_election_action()] {error_message} "
        f", POST={request.POST}"
    )
    context.update(get_list_of_elections())
    return render(request, 'elections/update_election/list_elections_to_modify.html', context)
