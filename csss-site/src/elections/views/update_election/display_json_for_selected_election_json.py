import json

from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.election_management import ELECTION_ID_SESSION_KEY, ELECTION_ID_POST_KEY, \
    JSON_INPUT_FIELD_POST_KEY
from elections.views.extractors.get_election_info_that_user_wants_to_modify_json import \
    get_information_for_election_user_wants_to_modify
from elections.views.utils.create_election_context import create_context


def display_current_election(request, context):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in json form, with possibly an
     error message
    """
    if ELECTION_ID_SESSION_KEY not in request.session:
        context[ERROR_MESSAGES_KEY] = ["Not all necessary fields were detected in your input"]
        return render(request, 'elections/update_election/update_election_json.html', context)
    context[ELECTION_ID_POST_KEY] = request.session[ELECTION_ID_SESSION_KEY]
    del request.session[ELECTION_ID_SESSION_KEY]

    election_dictionary, context[ERROR_MESSAGES_KEY] = \
        get_information_for_election_user_wants_to_modify(context[ELECTION_ID_POST_KEY])
    context[JSON_INPUT_FIELD_POST_KEY] = json.dumps(election_dictionary)
    return render(request, 'elections/update_election/update_election_json.html', context)
