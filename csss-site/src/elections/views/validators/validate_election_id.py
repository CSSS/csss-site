from elections.models import Election
from elections.views.Constants import ELECTION_ID


def validate_election_id(request_obj):
    """
    determine if the election ID in the object is a valid election ID tht maps to a single election

    Keyword Argument
    request_obj -- the dict that is checked for the election ID

    Return
    bool -- True or False to indicate if the election ID in the dict is valid
    """
    return ELECTION_ID in request_obj and f"{request_obj[ELECTION_ID]}".isdigit() and \
        (len(Election.objects.all().filter(id=int(request_obj[ELECTION_ID]))) == 1)
