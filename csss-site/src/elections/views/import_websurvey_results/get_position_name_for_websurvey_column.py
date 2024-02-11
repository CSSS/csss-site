from elections.models import NomineePosition


def get_position_name_for_websurvey_column(election_obj, voted_nominee_names):
    """
    Tries to ascertain if there is only 1 position that can possibly map to the choice of nominees indicated by
    votes_nominees for the election indicated by election_obj

    Keyword Arguments
    election_obj -- the election that is having its results imported
    voted_nominee_names -- the names of the nominees for a position that is ready to be finalized

    Return
    position_name -- either returns the position name if just 1 is relevant to all the voted_nominee_names,
     or it is None
    """
    potential_mappable_position_names = []
    for index, voted_nominee_name in enumerate(voted_nominee_names):
        potential_relevant_position_names = list(set(NomineePosition.objects.all().filter(
            nominee_speech__nominee__election_id=election_obj.id,
            nominee_speech__nominee__full_name=voted_nominee_name
        ).values_list('position_name', flat=True)))

        # narrow down current_list_of_relevant_position_names to the intersection between
        # potential_mappable_position_names and potential_relevant_position_names
        if len(potential_relevant_position_names) == 0:
            return None
        potential_mappable_position_names = [
            potential_relevant_position_name
            for potential_relevant_position_name in potential_relevant_position_names
            if (True if index == 0 else potential_relevant_position_name in potential_mappable_position_names)
        ]
    return potential_mappable_position_names[0] if len(potential_mappable_position_names) == 1 else None
