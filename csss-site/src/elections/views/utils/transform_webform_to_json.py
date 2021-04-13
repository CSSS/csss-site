import json
import logging

from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import ELECTION_NOMINEES_KEY, NOM_POSITION_AND_SPEECH_KEY, \
    NOM_POSITIONS_KEY, NOM_POSITION_KEY, NOM_ID_KEY

logger = logging.getLogger('csss_site')


def transform_webform_to_json(election_dict):
    """
    Converts the given election_dict into the same format that the JSON pages return

    Keyword Argument
    election_dict -- the dictionary that the webform creates

    Return
    election_dict -- the dictionary format that the JSON pages create
    """
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] transforming")
    logger.info(json.dumps(election_dict, indent=3))
    if ELECTION_NOMINEES_KEY in election_dict and type(election_dict[ELECTION_NOMINEES_KEY]) == dict:
        election_dict[ELECTION_NOMINEES_KEY] = list(election_dict[ELECTION_NOMINEES_KEY].values())
        for nominee in election_dict[ELECTION_NOMINEES_KEY]:
            if position_and_speech_pairing_dict_in_nominee_dict(nominee):
                nominee[NOM_POSITION_AND_SPEECH_KEY] = list(
                    nominee[NOM_POSITION_AND_SPEECH_KEY].values()
                )
                for speech in nominee[NOM_POSITION_AND_SPEECH_KEY]:
                    if NOM_POSITIONS_KEY in speech:
                        if there_are_multiple_entries(speech, NOM_POSITIONS_KEY):
                            positions = []
                            for position_info in speech[NOM_POSITIONS_KEY]:
                                position_info = position_info.split("_")
                                position_dict = {NOM_POSITION_KEY: position_info[0]}
                                if len(position_info) == 2 and f"{position_info[1]}".isdigit():
                                    position_dict[NOM_ID_KEY] = position_info[1]
                                    positions.append(position_dict)
                                else:
                                    positions.append(position_dict[NOM_POSITION_KEY])
                            speech[NOM_POSITIONS_KEY] = positions
                        else:
                            speech[NOM_POSITIONS_KEY] = [speech[NOM_POSITIONS_KEY]]
    logger.info("[elections/transform_webform_to_json.py transform_webform_to_json()] to")
    logger.info(json.dumps(election_dict, indent=3))
    return election_dict


def position_and_speech_pairing_dict_in_nominee_dict(nominee):
    return NOM_POSITION_AND_SPEECH_KEY in nominee and type(nominee[NOM_POSITION_AND_SPEECH_KEY]) == dict
