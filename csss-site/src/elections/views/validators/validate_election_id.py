from elections.models import Election
from elections.views.Constants import ELECTION_ID


def validate_election_id_in_dict(request_obj):
    """
    determine if the election ID in the object is a valid election ID tht maps to a single election

    Keyword Argument
    request_obj -- the dict that is checked for the election ID

    Return
    bool -- True or False to indicate if the election ID in the dict is valid
    """
    return ELECTION_ID in request_obj and validate_election_id(request_obj[ELECTION_ID])


def validate_election_id(election_id):
    """
    verify that the given election Id maps to a single election

    Keyword Argument
    election -- the election ID to verify

    Return
    bool -- True or False if the election id maps to a single election
    """
    return f"{election_id}".isdigit() and (len(Election.objects.all().filter(id=election_id))) == 1
