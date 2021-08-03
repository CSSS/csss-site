from csss.views_helper import there_are_multiple_entries
from elections.views.Constants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_JSON_KEY__NOM_POSITION_NAME, ID_KEY


def transform_nominee_webform_to_json(nominee):
    """
    converts the nominee dict from the webform into the form that the JSON also creates as that is the
     one that is more indigestable by the code

    Keyword Arguments:
    nominee -- the dict that contains the nominee info that will be updated
    """
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
            if ID_KEY in position_and_speech_pairing:
                if (
                        position_and_speech_pairing[ID_KEY] == "" or
                        not f"{position_and_speech_pairing[ID_KEY]}".isdigit()
                ):
                    del position_and_speech_pairing[ID_KEY]
