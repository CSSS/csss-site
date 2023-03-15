import json

from csss.setup_logger import Loggers
from elections.views.Constants import NA_STRING
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_INSTAGRAM, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, \
    ELECTION_JSON_KEY__NOM_SFUID, ELECTION_JSON_KEY__NOM_DISCORD_ID
from elections.views.utils.webform_to_json.transform_nominee_webform_to_json import transform_nominee_webform_to_json
from elections.views.utils.webform_to_json.transform_post_to_dictionary import transform_post_to_dictionary


def transform_nominee_links_webform_to_json(request, election_officer_request=True):
    """
    Converts the given request object into a JSON format to prepare for the
     process_nominee__nominee_links function

    Keyword Argument
    request -- the django request object
    election_officer_request -- indicates if the page is being accessed by the election officer

    Return
    new_nominee_dict -- the dictionary format that the process_nominee__nominee_links function takes in
    """
    logger = Loggers.get_logger()
    logger.info(
        "[elections/transform_nominee_links_webform_to_json.py "
        "transform_nominee_links_webform_to_json()] transforming"
    )
    nominee_dict = transform_post_to_dictionary(request)
    logger.info(json.dumps(nominee_dict, indent=3))
    new_nominee_dict = {}
    if ELECTION_JSON_KEY__NOMINEES in nominee_dict:
        new_nominee_dict = nominee_dict[ELECTION_JSON_KEY__NOMINEES][0]
    if ELECTION_JSON_KEY__NOM_FACEBOOK in new_nominee_dict:
        if new_nominee_dict[ELECTION_JSON_KEY__NOM_FACEBOOK] == NA_STRING:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_FACEBOOK] = None
        else:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_FACEBOOK] = \
                new_nominee_dict[ELECTION_JSON_KEY__NOM_FACEBOOK].strip()
    if ELECTION_JSON_KEY__NOM_INSTAGRAM in new_nominee_dict:
        if new_nominee_dict[ELECTION_JSON_KEY__NOM_INSTAGRAM] == NA_STRING:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_INSTAGRAM] = None
        else:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_INSTAGRAM] = \
                new_nominee_dict[ELECTION_JSON_KEY__NOM_INSTAGRAM].strip()
    if ELECTION_JSON_KEY__NOM_LINKEDIN in new_nominee_dict:
        if new_nominee_dict[ELECTION_JSON_KEY__NOM_LINKEDIN] == NA_STRING:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_LINKEDIN] = None
        else:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_LINKEDIN] = \
                new_nominee_dict[ELECTION_JSON_KEY__NOM_LINKEDIN].strip()
    if ELECTION_JSON_KEY__NOM_EMAIL in new_nominee_dict:
        if new_nominee_dict[ELECTION_JSON_KEY__NOM_EMAIL] == NA_STRING:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_EMAIL] = None
        else:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_EMAIL] = new_nominee_dict[ELECTION_JSON_KEY__NOM_EMAIL].strip()
    if ELECTION_JSON_KEY__NOM_DISCORD_ID in new_nominee_dict:
        new_nominee_dict[ELECTION_JSON_KEY__NOM_DISCORD_ID] = \
            new_nominee_dict[ELECTION_JSON_KEY__NOM_DISCORD_ID].strip()
    if election_officer_request:
        if ELECTION_JSON_KEY__NOM_SFUID in new_nominee_dict:
            new_nominee_dict[ELECTION_JSON_KEY__NOM_SFUID] = new_nominee_dict[ELECTION_JSON_KEY__NOM_SFUID].strip()
    else:
        new_nominee_dict[ELECTION_JSON_KEY__NOM_SFUID] = None
    transform_nominee_webform_to_json(new_nominee_dict)
    logger.info("[elections/transform_nominee_links_webform_to_json.py transform_nominee_links_webform_to_json()] to")
    logger.info(json.dumps(new_nominee_dict, indent=3))
    return new_nominee_dict
