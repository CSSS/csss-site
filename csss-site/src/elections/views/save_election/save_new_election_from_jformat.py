import datetime

from csss.setup_logger import get_logger
from elections.views.Constants import DATE_AND_TIME_FORMAT
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election
from elections.views.save_election.save_new_election_obj_jformat import create_and_save_election_object_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat

logger = get_logger()


def save_new_election_from_jformat(updated_elections_information, json=True):
    """
    extract all the information for the election and passes them off to
    create_and_save_election_object_jformat and save_new_or_update_existing_nominees_jformat to create the
    election object and the nominees

    Keyword Argument
    updated_elections_information -- the POST section of request
    json -- the bool that indicate whether the POST came from webform or JSON as that determines how to extract
     the date and time for the JSON

    Return
    the election obj
    """
    election_type = updated_elections_information[ELECTION_JSON_KEY__ELECTION_TYPE]
    election_websurvey = updated_elections_information[ELECTION_JSON_KEY__WEBSURVEY]
    if json:
        election_date = datetime.datetime.strptime(
            f"{updated_elections_information[ELECTION_JSON_KEY__DATE]}", DATE_AND_TIME_FORMAT
        )
    else:
        date_and_time = f"{updated_elections_information[ELECTION_JSON_KEY__DATE]} " \
                        f"{updated_elections_information[ELECTION_JSON_WEBFORM_KEY__TIME]}"
        election_date = datetime.datetime.strptime(
            date_and_time, DATE_AND_TIME_FORMAT
        )
    slug, human_friendly_name = gete_slug_and_human_friendly_name_election(election_date, election_type)
    election = create_and_save_election_object_jformat(election_type, election_websurvey, election_date, slug,
                                                       human_friendly_name)
    save_new_or_update_existing_nominees_jformat(election, updated_elections_information)
    logger.info(
        "[elections/save_new_election_from_jformat.py save_new_election_from_jformat()] election "
        f"{election} created with slug {election.slug}, "
        f"election_type={election.election_type}, date={election.date}, "
        f"websurvey={election.websurvey}, human_friendly_name={election.human_friendly_name} "
    )
    return election
