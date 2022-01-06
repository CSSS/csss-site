import json
import logging

from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES
from elections.views.utils.webform_to_json.copy_election_info_from_webform_to_json import \
    copy_election_info_from_webform_to_json
from elections.views.utils.webform_to_json.transform_nominee_webform_to_json import transform_nominee_webform_to_json

logger = logging.getLogger('csss_site')


def transform_webform_to_json(election_dict):
    """
    Converts the given election_dict from webform into the same format that the JSON pages return

    Keyword Argument
    election_dict -- the dictionary that the webform creates

    Return
    new_election_dict -- the dictionary format that the JSON pages create
    """
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] transforming")
    logger.info(json.dumps(election_dict, indent=3))
    new_election_dict = {}
    if ELECTION_JSON_KEY__NOMINEES in election_dict and type(election_dict[ELECTION_JSON_KEY__NOMINEES]) == dict:
        new_election_dict[ELECTION_JSON_KEY__NOMINEES] = list(election_dict[ELECTION_JSON_KEY__NOMINEES].values())
        for nominee in new_election_dict[ELECTION_JSON_KEY__NOMINEES]:  # type: list
            transform_nominee_webform_to_json(nominee)
    copy_election_info_from_webform_to_json(new_election_dict, election_dict)
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] to")
    logger.info(json.dumps(new_election_dict, indent=3))
    return new_election_dict
