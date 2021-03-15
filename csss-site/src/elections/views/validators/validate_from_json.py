import datetime
import json
import logging

from elections.models import Election

logger = logging.getLogger('csss_site')


def validate_and_return_election_json(input_json):
    try:
        election_json = json.loads(input_json)
        return True, None, election_json
    except json.decoder.JSONDecodeError as e:
        error_messages = f"Unable to decode the input due to error: {e}"
        logger.info(
            "[elections/validate_from_json.py validate_inputted_election_json()] "
            f"{error_messages}"
        )
        return False, [error_messages], \
               json.dumps(
                   input_json
               ).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")


def validate_election_type(election_type):
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    if election_type not in valid_election_type_choices:
        error_message = f"election_type of {election_type} is not one of the valid options."
        logger.error(
            "[elections/validate_from_json.py validate_inputted_election_json()]"
            f" {error_message}"
        )
        return False, error_message
    return True, None


def validate_election_date(date):
    try:
        datetime.datetime.strptime(f"{date}", '%Y-%m-%d %H:%M')
    except ValueError:
        error_message = f" given date of {date} is not in the valid format"
        logger.error(
            "[elections/validate_from_json.py validate_inputted_election_json()]"
            f"{error_message}"
        )
        return False, error_message
    except TypeError as e:
        error_message = "given date seems to be unreadable"
        logger.error(
            f"[elections/validate_from_json.py validate_inputted_election_json()]"
            f" {error_message} due to following error \n{e}"
        )
        return False, error_message
    return True, None