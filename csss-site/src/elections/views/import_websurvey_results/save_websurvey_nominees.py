from elections.models import PendingVoterChoice
from elections.views.Constants import SKIPPED_VOTE


def save_websurvey_nominees(index, election_obj, nominee_name, nominee_names):
    """
    Handles the saving of the data with the appropriate nominee name

    Keyword Arguments
    index -- the websurvey_column that user was in that indicates what position they were voter for
    election_obj -- the election that is having its results imported
    nomine_name -- the chosen option for the vote [in most cases the nominee name]
    nominee_names -- list of all the nominees that ran in the election as well as the No Confidence Vote and Skip Vote
    """
    nominee_name = nominee_name.strip()
    nominee_name = nominee_name if nominee_name != "" else SKIPPED_VOTE
    PendingVoterChoice(
        websurvey_column=index, full_name=nominee_name, election=election_obj,
        nominee_name_mapped=nominee_name in nominee_names
    ).save()
