import datetime

from elections.models import Election
from elections.views.Constants import DATE_AND_TIME_FORMAT
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_WEBFORM_KEY__TIME
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election


def validate_election_webform_format_uniqueness(election_dict, election_obj=None):
    """
    Validate that the election is unique in regard to its date and type

    Keyword Argument
    election_dict -- the dict that has the inputted election information
    election_obj -- the election object for the election that has to be displayed

    Return
    sucess -- Bool
    error_message -- an error message if the election is not unique, otherwise it is None
    """
    date_and_time = f"{election_dict[ELECTION_JSON_KEY__DATE]} {election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}"
    return validate_election_uniqueness(date_and_time, election_dict, election_obj=election_obj)


def validate_election_json_uniqueness(election_dict, election_obj=None):
    """
    Validate that the election is unique in regard to its date and type

    Keyword Argument
    election_dict -- the dict that has the inputted election information
    election_obj -- the election object for the election that has to be displayed

    Return
    sucess -- Bool
    error_message -- an error message if the election is not unique, otherwise it is None
    """
    return validate_election_uniqueness(election_dict[ELECTION_JSON_KEY__DATE], election_dict,
                                        election_obj=election_obj)


def validate_election_uniqueness(date_and_time, election_dict, election_obj=None):
    election_date = datetime.datetime.strptime(date_and_time, DATE_AND_TIME_FORMAT)
    election_type = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    slug, human_friendly_election_name = gete_slug_and_human_friendly_name_election(election_date, election_type)
    elections = Election.objects.all().filter(slug=slug)
    if election_obj is not None:
        elections = elections.exclude(id=election_obj.id)
    if len(elections) == 0:
        return True, None
    else:
        return False, f"there is already a page for {human_friendly_election_name}"
