import re

from about.views.input_new_officers.enter_new_officer_info.utils.get_sfu_info import get_sfu_info
from csss.views.time_converter import create_pst_time
from elections.models import NomineeLink
from elections.views.Constants import NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS, NA_STRING
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__END_DATE
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election
from elections.views.save_election.save_new_election_obj_jformat import create_and_save_election_object_jformat


def save_new_election_and_nominee_links(election_dict):
    election_type = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    election_websurvey = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    date_and_time = f"{election_dict[ELECTION_JSON_KEY__DATE]} " \
                    f"{election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}"
    election_date = re.split(r'-|:| ', date_and_time)
    year = int(election_date[0])
    month = int(election_date[1])
    day = int(election_date[2])
    hour_24 = int(election_date[3])
    minute = int(election_date[4])
    election_date = create_pst_time(year=year, month=month, day=day, hour_24=hour_24, minute=minute)
    end_date = re.split(r'-|:| ', f"{election_dict[ELECTION_JSON_KEY__END_DATE]}")
    year = int(end_date[0])
    month = int(end_date[1])
    day = int(end_date[2])
    election_end_date = create_pst_time(year=year, month=month, day=day)
    slug, human_friendly_name = gete_slug_and_human_friendly_name_election(election_date, election_type)
    election = create_and_save_election_object_jformat(
        election_type, election_websurvey, election_date, election_end_date, slug, human_friendly_name
    )
    for sfuid_and_discord_ids in election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS].split("\r\n"):
        sfuid = sfuid_and_discord_ids.split(",")[0]
        discord_id = sfuid_and_discord_ids.split(",")[1]
        success, error_message, sfu_info = get_sfu_info(sfuid)
        full_name = f"{sfu_info['firstnames']} {sfu_info['lastname']}" if success else NA_STRING
        nominee_link = NomineeLink(election=election, sfuid=sfuid, discord_id=discord_id, full_name=full_name)
        nominee_link.save()
        nominee_link.send_dm()
    return election
