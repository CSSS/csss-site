from django.shortcuts import render

from elections.views.Constants import ELECTION_ID
from elections.views.create_context.webform.create_webform_context import \
    create_webform_election_context_from_db_election_obj


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

    election_id = request.session[ELECTION_ID] if ELECTION_ID in request.session else request.POST[ELECTION_ID]
    if ELECTION_ID in request.session:
        del request.session[ELECTION_ID]
    context.update(create_webform_election_context_from_db_election_obj(election_id))
    return render(request, 'elections/update_election/update_election_webform.html', context)
