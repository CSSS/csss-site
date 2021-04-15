from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants import DISPLAY_ELECTION_KEY, ELECTION_ID_KEY
from elections.views.extractors.json.get_election_info_that_user_wants_to_modify_json import \
    get_information_for_election_user_wants_to_modify_in_json


def display_current_json_election_json(request, context):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in json form, with possibly an
     error message
    """
    if not (DISPLAY_ELECTION_KEY in request.POST or ELECTION_ID_KEY in request.POST):
        context[ERROR_MESSAGES_KEY] = ["Unable to locate the Election ID in the request"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    election_id = request.POST[DISPLAY_ELECTION_KEY] if DISPLAY_ELECTION_KEY in request.POST else request.POST[ELECTION_ID_KEY]
    context.update(get_information_for_election_user_wants_to_modify_in_json(election_id))
    return render(request, 'elections/update_election/update_election_json.html', context)
