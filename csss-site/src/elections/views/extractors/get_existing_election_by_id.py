import logging

from elections.models import Election
from elections.views.validators.validate_election_id import validate_election_id

logger = logging.getLogger('csss_site')


def get_existing_election_by_id(election_id):
    """Returns an election page by id

    Keyword Argument
    election_id -- the id for the election to return

    Return
    elections -- the election object for the election the user wants
    """
    logger.info(f"[elections/get_existing_election_by_id.py get_existing_election_by_id()] "
                f"trying to get election from ID {election_id} "
                )
    success, error_message = validate_election_id(election_id)
    if success:
        return Election.objects.get(id=election_id)
    logger.info("[elections/get_existing_election_by_id.py get_existing_election_by_id()] "
                f"unable to find an election by id '{election_id}'")
    return None
