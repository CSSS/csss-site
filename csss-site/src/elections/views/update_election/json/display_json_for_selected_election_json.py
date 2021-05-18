from django.shortcuts import render

from elections.views.Constants import ELECTION_ID
from elections.views.create_context.json.create_json_context import \
    create_json_election_context_from_user_inputted_election_dict, \
    create_json_election_context_from_db_election_obj
from elections.views.validators.validate_election_id import validate_election_id


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
    election_id_is_valid = False
    election_id = None
    if ELECTION_ID in request.session:
        election_id_is_valid = validate_election_id(request.session[ELECTION_ID])
        if election_id_is_valid:
            election_id = int(request.session[ELECTION_ID])
        del request.session[ELECTION_ID]
    elif ELECTION_ID in request.POST:
        election_id_is_valid = validate_election_id(request.POST[ELECTION_ID])
        if election_id_is_valid:
            election_id = int(request.POST[ELECTION_ID])
    error_message = None if election_id_is_valid is True else "No valid election found for given election id"
    context.update(create_json_election_context_from_user_inputted_election_dict(
        create_new_election=False,
        error_message=error_message,
        election_id=election_id,
        election_information=create_json_election_context_from_db_election_obj(election_id)
    ))
    return render(request, 'elections/update_election/update_election_json.html', context)
