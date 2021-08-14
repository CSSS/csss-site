from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__NOMINEES


def all_relevant_election_json_keys_exist(election_dict):
    """
    Ensures that all the necessary keys exist in the dict that was obtained from JSON page

    Keyword Argument
    election_dict -- the dict that was entered by user

    Return
    Bool -- True or False to indicate if all the necessary keys exist
    """
    return (
            ELECTION_JSON_KEY__ELECTION_TYPE in election_dict and ELECTION_JSON_KEY__DATE in election_dict and
            ELECTION_JSON_KEY__WEBSURVEY in election_dict and ELECTION_JSON_KEY__NOMINEES in election_dict
    )
