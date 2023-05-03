import re

from csss.setup_logger import Loggers
from csss.views.time_converter import create_pst_time
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election


def update_existing_election_obj_from_jformat(election, date, end_date_str, election_type, websurvey_link):
    """
    updates the election info

    Keyword Argument:
    election -- the Election object to update
    date -- the new day of the election
    end_date_str -- the new end date of the election
    election_type -- the updated election type
    websurvey_link -- the updated link to the websurvey
    """
    logger = Loggers.get_logger()
    date_and_time = re.split(r'-|:| ', date)
    year = int(date_and_time[0])
    month = int(date_and_time[1])
    day = int(date_and_time[2])
    hour = int(date_and_time[3])
    minute = int(date_and_time[4])
    election.date = create_pst_time(year=year, month=month, day=day, hour_24=hour, minute=minute)
    if end_date_str != "":
        end_date = re.split(r'-|:| ', end_date_str)
        year = int(end_date[0])
        month = int(end_date[1])
        day = int(end_date[2])
        election.end_date = create_pst_time(year=year, month=month, day=day)
    else:
        election.end_date = None
    election.slug, election.human_friendly_name = \
        gete_slug_and_human_friendly_name_election(election.date, election_type)
    election.election_type = election_type
    election.websurvey = websurvey_link
    logger.info(f"[elections/save_existing_election_obj_jformat.py update_existing_election_obj_from_jformat()] "
                f"updating election object {election} with date {date}, election_type {election_type} "
                f"websurvey link {websurvey_link}, slug {election.slug} and "
                f"human friendly name {election.human_friendly_name} "
                )
    election.save()
