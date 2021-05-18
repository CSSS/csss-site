import logging

from elections.models import Election

logger = logging.getLogger('csss_site')


def validate_election_type(election_type):
    """
    validates the election type

    Keyword Argument
    election_type -- the election type the user entered

    Return
    sucess -- Bool
    error_message -- an error message if the election type is incorrect, otherwise it is None
    """
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    if election_type not in valid_election_type_choices:
        error_message = f"election_type of \"{election_type}\" is not one of the valid options."
        logger.error(
            "[elections/validate_election_type.py validate_election_type()]"
            f" {error_message}"
        )
        return False, error_message
    return True, None
