from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES


def verify_that_all_relevant_election_webform_keys_exist(election_dict):
    return (ELECTION_JSON_KEY__DATE in election_dict and ELECTION_JSON_WEBFORM_KEY__TIME in election_dict and
            ELECTION_JSON_KEY__ELECTION_TYPE in election_dict and
            ELECTION_JSON_KEY__WEBSURVEY in election_dict and ELECTION_JSON_KEY__NOMINEES in election_dict)
