from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election
from elections.views.Constants_v2 import TYPES_OF_ELECTIONS, ELECTION_JSON_KEY__ELECTION_TYPE, VALID_POSITION_NAMES


def create_json_context():
    """
    Creating context for JSON pages for election creation or modification

    returns a dict with the following keys
    types_of_elections : "Options for...."
    valid_position_names : "Valid Positions: ...."
    """
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    current_positions = [
        position.position_name for position in OfficerEmailListAndPositionMapping.objects.all().filter(
            marked_for_deletion=False
        )
    ]
    return {
        TYPES_OF_ELECTIONS: f"Options for \"{ELECTION_JSON_KEY__ELECTION_TYPE}\": {', '.join(valid_election_type_choices)}",
        VALID_POSITION_NAMES: f"Valid Positions: {', '.join(current_positions)}",
    }
