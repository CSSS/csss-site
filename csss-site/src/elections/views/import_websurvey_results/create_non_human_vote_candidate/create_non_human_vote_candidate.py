from about.models import OfficerEmailListAndPositionMapping
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import NO_CONFIDENCE_NAME, SKIPPED_VOTE, CONFIDENCE_STRING


def create_non_human_vote_candidate(election_obj, pending_voter_choice, websurvey_column_position_mapping):
    """
    Create the Non-Human NomineePosition object for either a No Confidenec Vote or a Skipped Vote for the
     specified position

    Keyword Arguments
    election_obj -- the election that is having its results imported
    pending_voter_choice -- the PendingVoterChoice object that is for the non-human vote that is being finalized
    websurvey_column_position_mapping -- the WebsurveyColumnPositionMapping that corresponds to the column in
     pending_voter_choice

    Return
    non_human_candidate_position -- the non-human NomineePosition object that corresponds to pending_voter_choice
    """
    string_that_name_contains = (
        CONFIDENCE_STRING if pending_voter_choice.full_name == NO_CONFIDENCE_NAME else SKIPPED_VOTE
    )
    candidate_name = NO_CONFIDENCE_NAME if pending_voter_choice.full_name == NO_CONFIDENCE_NAME else SKIPPED_VOTE
    non_human_candidate = Nominee.objects.filter(
        election=election_obj,
        full_name__icontains=string_that_name_contains
    ).first()
    if non_human_candidate is None:
        non_human_candidate = Nominee(full_name=candidate_name, election=election_obj, human_candidate=False)
        non_human_candidate.save()
    non_human_candidate_speech = NomineeSpeech.objects.filter(nominee=non_human_candidate).first()
    if non_human_candidate_speech is None:
        non_human_candidate_speech = NomineeSpeech(nominee=non_human_candidate)
        non_human_candidate_speech.save()
    non_human_candidate_position = NomineePosition.objects.filter(
        nominee_speech__nominee__election=election_obj,
        position_name=websurvey_column_position_mapping.position_name,
        nominee_speech__nominee__full_name=non_human_candidate.full_name
    ).first()
    if non_human_candidate_position is None:
        position_index = OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=websurvey_column_position_mapping.position_name
        ).first().position_index
        non_human_candidate_position = NomineePosition(
            nominee_speech=non_human_candidate_speech,
            position_name=websurvey_column_position_mapping.position_name,
            position_index=position_index
        )
        non_human_candidate_position.save()
    return non_human_candidate_position
