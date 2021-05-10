import logging

from elections.models import Election
from elections.views.Constants import ELECTION_ID

logger = logging.getLogger('csss_site')

def validate_election_id_in_dict(request_obj):
    """
    determine if the election ID in the object is a valid election ID tht maps to a single election

    Keyword Argument
    request_obj -- the dict that is checked for the election ID

    Return
    bool -- True or False to indicate if the election ID in the dict is valid
    """
    election_id_present = ELECTION_ID in request_obj
    election_id_is_valid = False if election_id_present is False else validate_election_id(request_obj[ELECTION_ID])
    logger.info(
        "[elections/validate_election_id.py validate_election_id_in_dict()]"
        f"election_id_present = {election_id_present}, election_id_is_valid = {election_id_is_valid}"
    )
    return election_id_is_valid


def validate_election_id(election_id):
    """
    verify that the given election Id maps to a single election

    Keyword Argument
    election -- the election ID to verify

    Return
    bool -- True or False if the election id maps to a single election
    """
    election_id_is_digit = f"{election_id}".isdigit()
    election_id_is_valid = False if election_id_is_digit is False else (len(Election.objects.all().filter(id=election_id))) == 1
    logger.info(
        "[elections/validate_election_id.py validate_election_id()]"
        f"election_id of {election_id} has election_id_is_digit = {election_id_is_digit} and "
        f"election_id_is_valid = {election_id_is_valid}"
    )
    return election_id_is_valid
