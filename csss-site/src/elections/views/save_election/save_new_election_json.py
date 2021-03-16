import logging

from elections.models import Election

logger = logging.getLogger('csss_site')


def create_and_save_election_object(election_type, election_websurvey, election_date, slug, human_friendly_name):
    """
    Create a new election given the election information

    Keyword Arguments
    election_type -- indicates whether the election is a general election of by election
    election_websurvey -- the link to the election's websurvey
    election_date - the date and time of the election
    slug - the url for the election
    human_friendly_name -- the human friendly name of the election

    Return
    the election object

    """
    election = Election(slug=slug, election_type=election_type, date=election_date,
                        websurvey=election_websurvey, human_friendly_name=human_friendly_name)
    election.save()
    return election
