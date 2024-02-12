from elections.models import WebsurveyColumnPositionMapping, PendingVoterChoice, NomineePosition
from elections.views.Constants import NA_STRING


def get_dict_for_election_position_name_mapping(election_obj, pending_voter_choices, selected_position_mappings=None):
    """
    Created a list that has the dicts needed by elections/websurvey_results.html to determine which websurvey
     columns need to be mapped and the positions that can be mapped to them

    Keyword Arguments
     election_obj -- the election that is having its results imported
    pending_voter_choices -- list of all PendingVoterChoices objects for the selected election
    selected_position_mappings -- the dictionary that contains the positions that the user has so far selected
     for any websurvey column

    Return
    nominee_positions_mapping -- list where each element is
        {
            "websurvey_column": <0|1|2|....>,
            "relevant_positions": list of all position_names that can possible map to the websurvey_column for
             the selected election,
            "selected": position_name that the user has selected as the possible mapping for this column in the
             selected election
        }
    """
    nominee_positions_mapping = []
    mapped_websurvey_columns = list(WebsurveyColumnPositionMapping.objects.all().filter(
        election_id=election_obj.id
    ).values_list('websurvey_column', flat=True))
    results_positions = list(set(
        pending_voter_choices.exclude(websurvey_column__in=mapped_websurvey_columns).values_list(
            'websurvey_column', flat=True
        )
    ))
    results_positions.sort()
    for results_position in results_positions:
        voted_nominee_names = list(set(PendingVoterChoice.objects.all().filter(
            websurvey_column=results_position, election=election_obj
        ).values_list('full_name', flat=True)))

        draft_relevant_positions = list(set(NomineePosition.objects.all().order_by(
            'position_index'
        ).filter(
            nominee_speech__nominee__election_id=election_obj.id,
            nominee_speech__nominee__full_name__in=voted_nominee_names
        ).values_list('position_name', flat=True)))
        relevant_positions = []
        for draft_relevant_position in draft_relevant_positions:
            if draft_relevant_position not in relevant_positions:
                relevant_positions.append(draft_relevant_position)
        nominee_positions_mapping.append({
            "websurvey_question": results_position+1,
            "relevant_positions": relevant_positions,
            "selected": selected_position_mappings[results_position] if selected_position_mappings else NA_STRING
        })
    return nominee_positions_mapping
