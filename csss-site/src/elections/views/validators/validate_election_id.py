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
    error_message -- a potential error message if ID is not valid
    """
    if ELECTION_ID not in request_obj:
        error_message = "Unable to find an election ID in your request"
        logger.info(f"[elections/validate_election_id.py validate_election_id_in_dict()] {error_message}")
        return False, error_message
    return validate_election_id(request_obj[ELECTION_ID])


def validate_election_id(election_id):
    """
    verify that the given election Id maps to a single election

    Keyword Argument
    election -- the election ID to verify

    Return
    bool -- True or False if the election id maps to a single election
    error_message -- a potential error message if ID does not map to a single election
    """
    if not election_id:
        error_message = f"the detected election ID '{election_id}' is not a number"
        logger.info(f"[elections/validate_election_id.py validate_election_id()] {error_message}")
        return False, error_message
    if len(Election.objects.all().filter(id=election_id)) != 1:
        error_message = f"there is no election attached to ID '{election_id}'"
        logger.info(f"[elections/validate_election_id.py validate_election_id()] {error_message}")
        return False, error_message
    return True, None
