from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants import DISPLAY_ELECTION_KEY
from elections.views.extractors.webform.get_election_info_that_user_wants_to_modify_webform import \
    get_information_for_election_user_wants_to_modify_in_webform


def display_current_webform_election(request, context):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in WebForm form, with possibly an
     error message
    """
    if DISPLAY_ELECTION_KEY not in request.POST:
        context[ERROR_MESSAGES_KEY] = ["Unable to locate the Election ID in the request"]
        return render(request, 'elections/update_election/update_election_webform.html', context)
    context.update(get_information_for_election_user_wants_to_modify_in_webform(request.POST[DISPLAY_ELECTION_KEY]))
    return render(request, 'elections/update_election/update_election_webform.html', context)
