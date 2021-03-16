import json
import logging

logger = logging.getLogger('csss_site')


def validate_and_return_election_json(input_json):
    """
    Tries to create a dict from the JSON the user entered

    Keyword Argument
    input_json -- the JSON the user entered

    Return
    success -- Bool
    election -- either returns the election in DICT form or a tries its best for format the
     user's input into something that resembles a dict
    """
    try:
        election_json = json.loads(input_json)
        return True, None, election_json
    except json.decoder.JSONDecodeError as e:
        error_messages = f"Unable to decode the input due to error: {e}"
        logger.info(
            "[elections/validate_election_type.py validate_inputted_election_json()] "
            f"{error_messages}"
        )
        return False, [error_messages], \
               json.dumps(
                   input_json
               ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
