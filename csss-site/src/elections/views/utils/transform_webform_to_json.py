import json
import logging

from querystring_parser import parser

from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_POSITION_NAME, ID_KEY, ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_ID, ELECTION_JSON_KEY__NOMINEE, \
    SAVED_NOMINEE_LINKS, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS

logger = logging.getLogger('csss_site')




def transform_election_nominee_links_webform_to_json(election_dict):
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


def transform_nominee_links_webform_to_json(request):
    """
    Converts the given nominee dictionary from Nominee Link into a JSOn format to prepare for the
     process_nominee__nominee_links function

    Keyword Argument
    nominee_dict -- the dictionary that the nominee modification via link page created

    Return
    new_nominee_dict -- the dictionary format that the process_nominee__nominee_links function takes in
    """
    logger.info("[elections/transform_webform_to_json.py transform_nominee_links_webform_to_json()] transforming")
    nominee_dict = _transform_post_to_dictionary(request)
    logger.info(json.dumps(nominee_dict, indent=3))
    new_nominee_dict = {}
    if ELECTION_JSON_KEY__NOMINEE in nominee_dict:
        new_nominee_dict = nominee_dict[ELECTION_JSON_KEY__NOMINEE]
    _transform_nominee_webform_to_json(new_nominee_dict)
    logger.info("[elections/transform_webform_to_json.py transform_nominee_links_webform_to_json()] to")
    logger.info(json.dumps(new_nominee_dict, indent=3))
    return new_nominee_dict


def _transform_nominee_webform_to_json(nominee):
    if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee and \
            type(nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]) == dict:
        nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = list(
            nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].values()
        )
        for position_and_speech_pairing in nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]:
            if ELECTION_JSON_KEY__NOM_POSITION_NAMES in position_and_speech_pairing:
                if there_are_multiple_entries(position_and_speech_pairing,
                                              ELECTION_JSON_KEY__NOM_POSITION_NAMES):
                    positions = []
                    for position_info in position_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]:
                        position_info = position_info.split("_")
                        if len(position_info) == 2 and f"{position_info[1]}".isdigit():
                            positions.append(
                                {
                                    ELECTION_JSON_KEY__NOM_POSITION_NAME: position_info[0],
                                    ID_KEY: position_info[1]
                                }
                            )
                        else:
                            positions.append(position_info[0])
                    position_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = positions
                else:
                    position_info = position_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]
                    position_info = position_info.split("_")
                    if len(position_info) == 2 and f"{position_info[1]}".isdigit():
                        position_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = [
                            {
                                ELECTION_JSON_KEY__NOM_POSITION_NAME: position_info[0],
                                ID_KEY: position_info[1]
                            }
                        ]
                    else:
                        position_and_speech_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = \
                            [position_info[0]]


def _transform_post_to_dictionary(request):
    return parser.parse(request.POST.urlencode())


def _copy_election_info_from_webform_to_json(new_election_dict, election_dict):
    if ELECTION_JSON_KEY__DATE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__DATE] = election_dict[ELECTION_JSON_KEY__DATE]
    if ELECTION_JSON_WEBFORM_KEY__TIME in election_dict:
        new_election_dict[ELECTION_JSON_WEBFORM_KEY__TIME] = election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    if ELECTION_JSON_KEY__ELECTION_TYPE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__ELECTION_TYPE] = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    if ELECTION_JSON_KEY__WEBSURVEY in election_dict:
        new_election_dict[ELECTION_JSON_KEY__WEBSURVEY] = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
