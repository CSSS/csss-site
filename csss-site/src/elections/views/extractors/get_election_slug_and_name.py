import logging

from elections.models import Election
from elections.views.Constants import DATE_FORMAT

logger = logging.getLogger('csss_site')


def gete_slug_and_human_friendly_name_election(election_date, chosen_election_type):
    """
    create the slug and human friendly name for election using its date and election type

    Keyword Argument
    election_date -- the datetime for the election
    chosen_election_type -- indicates whether the election is a general election of by election

    Return
    slug -- the slug for the election
    human_friendly_name -- the human friendly name for the election
    """
    human_friendly_election_type = [
        valid_election_type_choice[1]
        for valid_election_type_choice in Election.election_type_choices
        if valid_election_type_choice[0] == chosen_election_type
    ][0]
    slug = f"{election_date.strftime(DATE_FORMAT)}-{chosen_election_type}"
    human_friendly_name = f"{human_friendly_election_type}: {election_date.strftime(DATE_FORMAT)}"
    logger.info(f"[elections/get_election_slug_and_name.py gete_slug_and_human_friendly_name_election()] "
                f"created slug of {slug} and human_friendly_name of {human_friendly_name} from election "
                f"date {election_date} and election_type of {chosen_election_type}"
                )
    return slug, human_friendly_name
