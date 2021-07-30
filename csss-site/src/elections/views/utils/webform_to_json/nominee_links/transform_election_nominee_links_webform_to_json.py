import json
import logging

from elections.views.Constants import SAVED_NOMINEE_LINKS, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS, \
    ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_KEY__WEBSURVEY
from elections.views.utils.webform_to_json.transform_post_to_dictionary import transform_post_to_dictionary

logger = logging.getLogger('csss_site')


def transform_election_nominee_links_webform_to_json(request):
    """
    Converts the given election info and nominee link dictionary from
     Webform into a JSON format to prepare for the
     process_existing_election_and_nominee_links function

    Keyword Argument
    nominee_dict -- the dictionary that the election modification page created

    Return
    new_nominee_dict -- the dictionary format that the process_existing_election_and_nominee_links function takes in
    """
    logger.info(
        "[elections/transform_webform_to_json.py transform_election_nominee_links_webform_to_json()] "
        "transforming"
    )
    election_dict = transform_post_to_dictionary(request)
    logger.info(json.dumps(election_dict, indent=3))
    new_nominee_dict = {}
    _copy_election_info_from_webform_to_json(new_nominee_dict, election_dict)
    if SAVED_NOMINEE_LINKS in election_dict:
        new_nominee_dict[SAVED_NOMINEE_LINKS] = list(election_dict[SAVED_NOMINEE_LINKS].values())
    if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict:
        new_nominee_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS] = election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
    logger.info("[elections/transform_webform_to_json.py transform_election_nominee_links_webform_to_json()] to")
    logger.info(json.dumps(new_nominee_dict, indent=3))
    return new_nominee_dict


def _copy_election_info_from_webform_to_json(new_election_dict, election_dict):
    if ELECTION_JSON_KEY__DATE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__DATE] = election_dict[ELECTION_JSON_KEY__DATE]
    if ELECTION_JSON_WEBFORM_KEY__TIME in election_dict:
        new_election_dict[ELECTION_JSON_WEBFORM_KEY__TIME] = election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    if ELECTION_JSON_KEY__ELECTION_TYPE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__ELECTION_TYPE] = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    if ELECTION_JSON_KEY__WEBSURVEY in election_dict:
        new_election_dict[ELECTION_JSON_KEY__WEBSURVEY] = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
