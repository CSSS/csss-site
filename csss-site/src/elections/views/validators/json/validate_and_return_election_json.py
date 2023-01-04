import json

from csss.setup_logger import Loggers
from elections.views.utils.prepare_json_for_html import prepare_json_for_html


def validate_and_return_election_json(input_json):
    """
    Tries to create a dict from the JSON the user entered

    Keyword Argument
    input_json -- the JSON the user entered

    Return
    success -- Bool
    error_message -- potential error message if unable to loads JSON into dict
    election -- either returns the election in DICT form or a tries its best for format the
     user's input into something that resembles a dict
    """
    logger = Loggers.get_logger()
    try:
        election_json = json.loads(input_json)
        return True, None, election_json
    except json.decoder.JSONDecodeError as e:
        error_messages = f"Unable to decode the input due to error: {e}"
        logger.info(
            "[elections/validate_and_return_election_json.py validate_and_return_election_json()] "
            f"{error_messages}"
        )
        return False, error_messages, prepare_json_for_html(input_json)
