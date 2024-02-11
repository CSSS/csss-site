from elections.models import PendingVoterChoice, WebsurveyColumnPositionMapping
from elections.views.Constants import SKIPPED_VOTE, NO_CONFIDENCE_NAME
from elections.views.import_websurvey_results.get_position_name_for_websurvey_column import \
    get_position_name_for_websurvey_column


def create_websurvey_column_position_mappings(election_obj):
    """
    Tries to determine any Websurvey Position Mappings that can be saved with the currently mapped PendingVoterChoice

    Keyword Arguments
    election_obj -- the election that is having its results imported
    """
    websurvey_columns_with_unmapped_nominee_names = list(set(PendingVoterChoice.objects.all().filter(
        nominee_name_mapped=False, election=election_obj
    ).values_list('websurvey_column', flat=True)))
    pending_voter_choices_ready_to_be_finalized = PendingVoterChoice.objects.all().filter(
        election=election_obj
    ).exclude(websurvey_column__in=websurvey_columns_with_unmapped_nominee_names).order_by('websurvey_column')
    previous_websurvey_column = None
    for pending_voter_choice_ready_to_be_finalized in pending_voter_choices_ready_to_be_finalized:
        websurvey_column = pending_voter_choice_ready_to_be_finalized.websurvey_column
        if websurvey_column == previous_websurvey_column:
            # skip to the next loop if the current websurvey_column has already been dealt with in some way
            continue
        websurvey_column_position_mapping = WebsurveyColumnPositionMapping.objects.all().filter(
            election=election_obj, websurvey_column=websurvey_column
        ).first()  # checking to see if this websurvey_column that is ready to be mapped is already mapped
        if websurvey_column_position_mapping is None:
            voted_nominee_names = list(set(pending_voter_choices_ready_to_be_finalized.filter(
                websurvey_column=websurvey_column
            ).exclude(full_name=NO_CONFIDENCE_NAME).exclude(
                full_name=SKIPPED_VOTE
            ).values_list('full_name', flat=True)))  # getting the list of all the nominees voted for the position
            # indicated by websurvey_column
            relevant_position_name = get_position_name_for_websurvey_column(election_obj, voted_nominee_names)
            if relevant_position_name:
                # there is only one position that seems to map to the websurvey_column given the nominees that had
                # votes cast for them for the position [ indicated by voted_nominees] so it's safe to determine the
                # mapping at this point
                WebsurveyColumnPositionMapping(
                    websurvey_column=websurvey_column, election=election_obj,
                    position_name=relevant_position_name
                ).save()
        previous_websurvey_column = websurvey_column
