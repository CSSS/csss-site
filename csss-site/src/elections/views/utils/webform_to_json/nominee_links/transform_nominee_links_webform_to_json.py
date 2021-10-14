import json
import logging

from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE
from elections.views.utils.webform_to_json.transform_nominee_webform_to_json import transform_nominee_webform_to_json
from elections.views.utils.webform_to_json.transform_post_to_dictionary import transform_post_to_dictionary

logger = logging.getLogger('csss_site')


def transform_nominee_links_webform_to_json(request):
    """
    Converts the given request object into a JSON format to prepare for the
     process_nominee__nominee_links function

    Keyword Argument
    request -- the django request object

    Return
    new_nominee_dict -- the dictionary format that the process_nominee__nominee_links function takes in
    """
    logger.info(
        "[elections/transform_nominee_links_webform_to_json.py "
        "transform_nominee_links_webform_to_json()] transforming"
    )
    nominee_dict = transform_post_to_dictionary(request)
    logger.info(json.dumps(nominee_dict, indent=3))
    new_nominee_dict = {}
    if ELECTION_JSON_KEY__NOMINEE in nominee_dict:
        new_nominee_dict = nominee_dict[ELECTION_JSON_KEY__NOMINEE][0]
    transform_nominee_webform_to_json(new_nominee_dict)
    logger.info("[elections/transform_nominee_links_webform_to_json.py transform_nominee_links_webform_to_json()] to")
    logger.info(json.dumps(new_nominee_dict, indent=3))
    return new_nominee_dict
