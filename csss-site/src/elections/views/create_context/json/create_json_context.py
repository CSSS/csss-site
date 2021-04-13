from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election
from elections.views.Constants import ELECTION_TYPE_KEY


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
        'types_of_elections': f"Options for \"{ELECTION_TYPE_KEY}\": {', '.join(valid_election_type_choices)}",
        'valid_position_names': f"Valid Positions: {', '.join(current_positions)}"
    }
