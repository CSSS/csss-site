import json

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants import ELECTION_DATE_KEY, ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, \
    ELECTION_NOMINEES_KEY, JSON_INPUT_FIELD_KEY, ELECTION_ID_KEY
from elections.views.extractors.get_election_nominees import get_election_nominees
from elections.views.extractors.get_existing_election_by_id import get_existing_election_by_id


def get_information_for_election_user_wants_to_modify_in_json(election_id):
    """
    Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    a dict that contains either the error experienced when trying to access the election id
    or the election itself in a format that is ready for the json page to display
    """
    election = get_existing_election_by_id(election_id)
    if election is None:
        return {
            ERROR_MESSAGES_KEY: ["No valid election found for given election id"]
        }
    return {
        ELECTION_ID_KEY: election_id,
        JSON_INPUT_FIELD_KEY: json.dumps(
            {
                ELECTION_DATE_KEY: election.date.strftime("%Y-%m-%d %H:%M"),
                ELECTION_TYPE_KEY: election.election_type,
                ELECTION_WEBSURVEY_LINK_KEY: election.websurvey,
                ELECTION_NOMINEES_KEY: get_election_nominees(election)
            }
        )
    }
