import datetime

from csss.setup_logger import Loggers
from csss.views.time_converter import create_pst_time_from_datetime
from csss.views_helper import DATE_FORMAT
from elections.views.Constants import DATE_AND_TIME_FORMAT
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__END_DATE
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election
from elections.views.save_election.save_new_election_obj_jformat import create_and_save_election_object_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat


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
    logger = Loggers.get_logger()
    election_type = updated_elections_information[ELECTION_JSON_KEY__ELECTION_TYPE]
    election_websurvey = updated_elections_information[ELECTION_JSON_KEY__WEBSURVEY]
    if json:
        election_date = datetime.datetime.strptime(
            f"{updated_elections_information[ELECTION_JSON_KEY__DATE]}", DATE_AND_TIME_FORMAT
        )
        election_date = create_pst_time_from_datetime(election_date)
        election_end_date = datetime.datetime.strptime(
            f"{updated_elections_information[ELECTION_JSON_KEY__END_DATE]}", DATE_FORMAT
        )
        election_end_date = create_pst_time_from_datetime(election_end_date)
    else:
        date_and_time = f"{updated_elections_information[ELECTION_JSON_KEY__DATE]} " \
                        f"{updated_elections_information[ELECTION_JSON_WEBFORM_KEY__TIME]}"
        election_date = datetime.datetime.strptime(
            date_and_time, DATE_AND_TIME_FORMAT
        )
        election_date = create_pst_time_from_datetime(election_date)

        end_date = f"{updated_elections_information[ELECTION_JSON_KEY__END_DATE]}"
        election_end_date = datetime.datetime.strptime(
            end_date, DATE_FORMAT
        )
        election_end_date = create_pst_time_from_datetime(election_end_date)

    slug, human_friendly_name = gete_slug_and_human_friendly_name_election(election_date, election_type)
    election = create_and_save_election_object_jformat(election_type, election_websurvey, election_date,
                                                       election_end_date, slug, human_friendly_name)
    save_new_or_update_existing_nominees_jformat(election, updated_elections_information)
    logger.info(
        "[elections/save_new_election_from_jformat.py save_new_election_from_jformat()] election "
        f"{election} created with slug {election.slug}, "
        f"election_type={election.election_type}, date={election.date}, "
        f"websurvey={election.websurvey}, human_friendly_name={election.human_friendly_name} "
    )
    return election
