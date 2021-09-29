from django.shortcuts import render

from elections.views.create_context.json.create_json_context import \
    create_json_election_context_from_user_inputted_election_dict, \
    create_json_election_context_from_db_election_obj


def display_current_json_election_json(request, election, context):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in json form, with possibly an
     error message
    """

    context.update(create_json_election_context_from_user_inputted_election_dict(
        create_new_election=False,
        election_information=create_json_election_context_from_db_election_obj(election)
    ))
    return render(request, 'elections/update_election/update_election_json.html', context)
