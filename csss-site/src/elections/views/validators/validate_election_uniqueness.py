import datetime

from elections.models import Election
from elections.views.Constants import DATE_AND_TIME_FORMAT
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_WEBFORM_KEY__TIME
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election


def validate_election_webform_format_uniqueness(election_dict):
    """
    Validate that the election is unique in regard to its date and type

    Keyword Argument
    date -- the inputted election date
    election_type -- the inputted election type

    Return
    sucess -- Bool
    error_message -- an error message if the election is not unique, otherwise it is None
    """
    date_and_time = f"{election_dict[ELECTION_JSON_KEY__DATE]} {election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}"
    return (True, None) if validate_election_uniqueness(date_and_time, election_dict) \
        else (False, f"there is already election of type {election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]} "
                     f"election for the date {election_dict[ELECTION_JSON_KEY__DATE]}")


def validate_election_json_uniqueness(election_dict):
    """
    Validate that the election is unique in regard to its date and type

    Keyword Argument
    date -- the inputted election date
    election_type -- the inputted election type

    Return
    sucess -- Bool
    error_message -- an error message if the election is not unique, otherwise it is None
    """
    date_and_time = f"{election_dict[ELECTION_JSON_KEY__DATE]}"
    return (True, None) if validate_election_uniqueness(date_and_time, election_dict) \
        else (False, f"there is already election of type {election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]} "
                     f"election for the date {election_dict[ELECTION_JSON_KEY__DATE]}")


def validate_election_uniqueness(date_and_time, election_dict):
    election_date = datetime.datetime.strptime(date_and_time, DATE_AND_TIME_FORMAT)
    election_type = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    return len(
        Election.objects.all().filter(slug=gete_slug_and_human_friendly_name_election(election_date, election_type)[0])
    ) == 0
