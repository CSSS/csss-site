from csss.setup_logger import get_logger
from elections.models import Election


def create_and_save_election_object_jformat(
        election_type, election_websurvey, election_date, slug, human_friendly_name):
    """
    Create a new election given the election information

    Keyword Arguments
    election_type -- indicates whether the election is a general election of by election
    election_websurvey -- the link to the election's websurvey
    election_date - the date and time of the election
    slug - the slug for the election
    human_friendly_name -- the human friendly name of the election

    Return
    the election object

    """
    logger = get_logger()
    election = Election(slug=slug, election_type=election_type, date=election_date,
                        websurvey=election_websurvey, human_friendly_name=human_friendly_name)
    election.save()
    logger.info(f"[elections/save_new_election_obj_jformat.py create_and_save_election_object_jformat()] "
                f"saving new election object {election} with date {election_date}, election_type {election_type} "
                f"websurvey link {election_websurvey}, slug {slug} and "
                f"human friendly name {human_friendly_name} "
                )
    return election
