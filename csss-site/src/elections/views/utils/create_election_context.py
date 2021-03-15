from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election
from elections.views.election_management import ELECTION_TYPE_KEY


def create_context():
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
