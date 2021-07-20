import json
import logging

from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_POSITION_NAME, ID_KEY, ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_ID

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
        for nominee in new_election_dict[ELECTION_JSON_KEY__NOMINEES]:
            if verify_that_position_and_speech_pairing_dict_is_in_nominee_dict(nominee):
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
    if ELECTION_JSON_KEY__DATE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__DATE] = election_dict[ELECTION_JSON_KEY__DATE]
    if ELECTION_JSON_WEBFORM_KEY__TIME in election_dict:
        new_election_dict[ELECTION_JSON_WEBFORM_KEY__TIME] = election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    if ELECTION_JSON_KEY__ELECTION_TYPE in election_dict:
        new_election_dict[ELECTION_JSON_KEY__ELECTION_TYPE] = election_dict[ELECTION_JSON_KEY__ELECTION_TYPE]
    if ELECTION_JSON_KEY__WEBSURVEY in election_dict:
        new_election_dict[ELECTION_JSON_KEY__WEBSURVEY] = election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    if ELECTION_ID in election_dict:
        new_election_dict[ELECTION_ID] = election_dict[ELECTION_ID]
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] to")
    logger.info(json.dumps(new_election_dict, indent=3))
    return new_election_dict


def verify_that_position_and_speech_pairing_dict_is_in_nominee_dict(nominee):
    return ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee and \
           type(nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]) == dict


def transform_nominee_links_webform_to_json(election_dict):
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] transforming")
    logger.info(json.dumps(election_dict, indent=3))
    new_election_dict = election_dict['nominee']
    if verify_that_position_and_speech_pairing_dict_is_in_nominee_dict(new_election_dict):
        new_election_dict[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = list(
            new_election_dict[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].values()
        )
        for position_and_speech_pairing in new_election_dict[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]:
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
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] to")
    logger.info(json.dumps(new_election_dict, indent=3))
    return new_election_dict