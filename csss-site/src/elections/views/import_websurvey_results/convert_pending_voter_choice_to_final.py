from elections.models import WebsurveyColumnPositionMapping, PendingVoterChoice, NomineePosition, VoterChoice
from elections.views.Constants import NO_CONFIDENCE_NAME, SKIPPED_VOTE
from elections.views.import_websurvey_results.create_non_human_vote_candidate.create_non_human_vote_candidate import \
    create_non_human_vote_candidate


def convert_pending_voter_choice_to_final(election_obj):
    """
    Iterate over all the WebsurveyColumnPositionMappings and convert the corresponding PendingVoterChoice to
     VoterChoice

    Keyword Arguments
    election_obj -- the election that is having its results imported

    Return
    bool -- True if all the pending_voter_choices that mapped to WebsurveyColumnPositionMapping were finalized,
     False otherwise
    pending_voter_choice_id -- None if true, the id of the problematic pending_voter_choice otherwise
    """
    websurvey_column_position_mappings = WebsurveyColumnPositionMapping.objects.all().filter(
        election=election_obj
    ).order_by('websurvey_column')
    for websurvey_column_position_mapping in websurvey_column_position_mappings:
        pending_voter_choices = PendingVoterChoice.objects.all().filter(
            websurvey_column=websurvey_column_position_mapping.websurvey_column, election=election_obj,
            nominee_name_mapped=True  # this filter should not technically be necessary but what the heck :shrug:
        )
        for pending_voter_choice in pending_voter_choices:
            nominee_position = NomineePosition.objects.all().filter(
                nominee_speech__nominee__election_id=election_obj.id,
                nominee_speech__nominee__full_name=pending_voter_choice.full_name,
                position_name=websurvey_column_position_mapping.position_name
            ).first()
            human_candidate = pending_voter_choice.full_name not in [NO_CONFIDENCE_NAME, SKIPPED_VOTE]
            if nominee_position:
                VoterChoice(selection=nominee_position).save()
                pending_voter_choice.delete()
            elif not human_candidate:
                non_human_candidate_position = create_non_human_vote_candidate(
                    election_obj, pending_voter_choice, websurvey_column_position_mapping
                )
                VoterChoice(selection=non_human_candidate_position).save()
                pending_voter_choice.delete()
            else:
                return False, pending_voter_choice.id
    return True, None
