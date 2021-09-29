from django.shortcuts import render

from elections.views.create_context.webform.create_webform_context import \
    create_webform_election_context_from_db_election_obj


def display_current_webform_election(request, election, context):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in WebForm form, with possibly an
     error message
    """

    context.update(create_webform_election_context_from_db_election_obj(election))
    return render(request, 'elections/update_election/update_election__webform.html', context)
