import logging

from elections.models import Nominee

logger = logging.getLogger('csss_site')

def get_exist_nominee(nominee_id, election_id):
    """
    Gets the Nominee object that maps to the specified IDs

    Keyword Argument:
    nominee_id -- the ID of the Nominee object to obtain
    election_id -- the ID of the election that the nominee is running in

    Return
    Nominee -- the nominee object or None if no matching nominees found
    """
    logger.info(f"[elections/get_existing_nominee.py get_exist_nominee()] "
                f"trying to get nominee with ID {nominee_id} from election with id {election_id} "
                )
    nominees = Nominee.objects.all().filter(election_id=election_id, id=nominee_id)
    if len(nominees) != 1:
        logger.info(f"[elections/get_existing_nominee.py get_exist_nominee()] "
                    f"no nominee was found "
                    )
        return None
    return nominees[0]
