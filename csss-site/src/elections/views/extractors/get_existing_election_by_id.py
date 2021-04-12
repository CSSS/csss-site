import logging

from elections.models import Election

logger = logging.getLogger('csss_site')


def get_existing_election_by_id(election_id):
    """Returns an election page by id

    Keyword Argument
    election_id -- the id for the election to return

    Return
    elections -- the election object for the election the user wants
    """
    try:
        elections = Election.objects.get(id=election_id)
    except Exception:
        logger.info("[elections/get_existing_election_by_id.py get_existing_election_by_id()] "
                    f"unable to find an election by id '{election_id}'")
        return None
    return elections
