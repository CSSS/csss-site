from django.shortcuts import render

from elections.views.Constants import ELECTION_ID_KEY
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
    election_id = request.session[ELECTION_ID_KEY]
    del request.session[ELECTION_ID_KEY]
    context.update(get_information_for_election_user_wants_to_modify_in_webform(election_id))
    return render(request, 'elections/update_election/update_election_webform.html', context)
