import datetime
import logging

from elections.views.election_management import ELECTION_TYPE_POST_KEY, ELECTION_WEBSURVEY_LINK_POST_KEY, \
    ELECTION_DATE_POST_KEY
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election
from elections.views.save_election.save_new_election_json import create_and_save_election_object
from elections.views.save_nominee.save_new_or_update_existing_nominees import save_new_or_update_existing_nominees

logger = logging.getLogger('csss_site')


def save_new_election_from_json(updated_elections_information):
    """
    extract all the information for the election [excluding the datetime] and passes them off to
    create_and_save_election_object and save_new_or_update_existing_nominees to create the
    election object and the nominees

    Keyword Argument
    updated_elections_information -- the POST section of request

    Return
    the election slug
    """
    election_type = updated_elections_information[ELECTION_TYPE_POST_KEY]
    election_websurvey = updated_elections_information[ELECTION_WEBSURVEY_LINK_POST_KEY]
    election_date = datetime.datetime.strptime(
        f"{updated_elections_information[ELECTION_DATE_POST_KEY]}", '%Y-%m-%d %H:%M'
    )
    slug, human_friendly_name = gete_slug_and_human_friendly_name_election(election_date, election_type)
    election = create_and_save_election_object(election_type, election_websurvey, election_date, slug,
                                               human_friendly_name)
    save_new_or_update_existing_nominees(election, updated_elections_information)
    logger.info(
        "[elections/extract_from_json.py save_new_election_from_json()] election "
        f"{election} created with slug {election.slug}, "
        f"election_type={election.election_type}, date={election.date}, "
        f"websurvey={election.websurvey}, human_friendly_name={election.human_friendly_name} "
    )
    return election.slug
