from elections.views.Constants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY


def copy_election_info_from_webform_to_json(new_election_dict, election_dict):
    if ELECTION_JSON_KEY__DATE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__DATE] = election_dict[ELECTION_JSON_KEY__DATE]
    if ELECTION_JSON_WEBFORM_KEY__TIME in election_dict:
        new_election_dict[ELECTION_JSON_WEBFORM_KEY__TIME] = election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    if ELECTION_JSON_KEY__ELECTION_TYPE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__ELECTION_TYPE] = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    if ELECTION_JSON_KEY__WEBSURVEY in election_dict:
        new_election_dict[ELECTION_JSON_KEY__WEBSURVEY] = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
